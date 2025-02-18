/*
 *  SLAMTEC LIDAR
 *  Ultra Simple Data Grabber Demo App
 *
 *  Copyright (c) 2009 - 2014 RoboPeak Team
 *  http://www.robopeak.com
 *  Copyright (c) 2014 - 2020 Shanghai Slamtec Co., Ltd.
 *  http://www.slamtec.com
 *
 */
/*
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <string.h>
#include <fstream>
#include <cstring>
#include <errno.h>
#include <fcntl.h>
#include <iostream>
#include <termios.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include "sl_lidar.h" 
#include "sl_lidar_driver.h"

// Add at top of file
#include <tuple>
#include <mutex>
#include <atomic>
#include <deque>
#include <chrono>
#include <cmath>

std::mutex imu_mutex;
std::deque<std::tuple<int64_t, std::string>> imu_data_queue;
std::fstream fout;

#ifndef _countof
#define _countof(_Array) (int)(sizeof(_Array) / sizeof(_Array[0]))
#endif

#ifdef _WIN32
#include <Windows.h>
#define delay(x)   ::Sleep(x)
#else
#include <unistd.h>
static inline void delay(sl_word_size_t ms){
    while (ms>=1000){
        usleep(1000*1000);
        ms-=1000;
    };
    if (ms!=0)
        usleep(ms*1000);
}
#endif

using namespace sl;

void handle_timeout(int sig) {
    std::cerr << "\nTimeout while attempting to open port." << std::endl;
    signal(sig, SIG_IGN);
}

void print_usage(int argc, const char * argv[])
{
    printf("Usage:\n"
           " For serial channel\n %s --channel --serial <com port> [baudrate]\n"
           " The baudrate used by different models is as follows:\n"
           "  A1(115200),A2M7(256000),A2M8(115200),A2M12(256000),"
           "A3(256000),S1(256000),S2(1000000),S3(1000000)\n"
		   " For udp channel\n %s --channel --udp <ipaddr> [port NO.]\n"
           " The T1 default ipaddr is 192.168.11.2,and the port NO.is 8089. Please refer to the datasheet for details.\n"
           , argv[0], argv[0]);
}

bool checkSLAMTECLIDARHealth(ILidarDriver * drv)
{
    sl_result     op_result;
    sl_lidar_response_device_health_t healthinfo;

    op_result = drv->getHealth(healthinfo);
    if (SL_IS_OK(op_result)) { // the macro IS_OK is the preperred way to judge whether the operation is succeed.
        printf("SLAMTEC Lidar health status : %d\n", healthinfo.status);
        if (healthinfo.status == SL_LIDAR_STATUS_ERROR) {
            fprintf(stderr, "Error, slamtec lidar internal error detected. Please reboot the device to retry.\n");
            // enable the following code if you want slamtec lidar to be reboot by software
            // drv->reset();
            return false;
        } else {
            return true;
        }

    } else {
        fprintf(stderr, "Error, cannot retrieve the lidar health code: %x\n", op_result);
        return false;
    }
}

bool ctrl_c_pressed;
void ctrlc(int)
{
    ctrl_c_pressed = true;
}

std::string current_serial_data = "0";
std::mutex serial_mutex;
std::atomic<bool> should_run{true};
bool hasNewData = false;
std::string lastSerialData = "";

void storeIMUData(const std::string& imu_reading) {
    auto now = std::chrono::system_clock::now();
    int64_t time_ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();

    std::lock_guard<std::mutex> lock(imu_mutex);
    imu_data_queue.emplace_back(time_ms, imu_reading); // Push to back

    // Keep only the last 10 readings
    while (imu_data_queue.size() > 2) {
        imu_data_queue.pop_front(); // Remove oldest
    }
}

std::string getClosestIMUReading(int64_t lidar_timestamp) {
    std::lock_guard<std::mutex> lock(imu_mutex);

    if (imu_data_queue.empty()) return "NoData";

    auto closest = imu_data_queue.front();
    int64_t min_diff = std::abs(std::get<0>(closest) - lidar_timestamp);

    for (const auto& entry : imu_data_queue) { // Now we can iterate!
        int64_t diff = std::abs(std::get<0>(entry) - lidar_timestamp);
        if (diff < min_diff) {
            closest = entry;
            min_diff = diff;
        }
    }
    std::string imu_values = std::get<1>(closest);
    imu_values.erase(std::remove(imu_values.begin(), imu_values.end(), '\n'), imu_values.end());

    return std::get<1>(closest);
}


void writeLidarData(int angle, int distance) {
    
    auto now = std::chrono::system_clock::now();
    int64_t lidar_time_ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();

    std::string imu_reading = getClosestIMUReading(lidar_time_ms);
    
    fout << lidar_time_ms << "," << angle << "," << distance << "," << imu_reading << std::endl;
}

int main(int argc, const char * argv[]) {
	const char * opt_is_channel = NULL; 
	const char * opt_channel = NULL;
    const char * opt_channel_param_first = NULL;
	sl_u32         opt_channel_param_second = 0;
    sl_u32         baudrateArray[2] = {115200, 256000};
    sl_result     op_result;
	int          opt_channel_type = CHANNEL_TYPE_SERIALPORT;

	bool useArgcBaudrate = false;

    IChannel* _channel;

    printf("Ultra simple LIDAR data grabber for SLAMTEC LIDAR.\n"
           "Version: %s\n", SL_LIDAR_SDK_VERSION);

	 
	if (argc>1)
	{ 
		opt_is_channel = argv[1];
	}
	else
	{
		print_usage(argc, argv);
		return -1;
	}

	if(strcmp(opt_is_channel, "--channel")==0){
		opt_channel = argv[2];
		if(strcmp(opt_channel, "-s")==0||strcmp(opt_channel, "--serial")==0)
		{
			// read serial port from the command line...
			opt_channel_param_first = argv[3];// or set to a fixed value: e.g. "com3"
			// read baud rate from the command line if specified...
			if (argc>4) opt_channel_param_second = strtoul(argv[4], NULL, 10);	
			useArgcBaudrate = true;
		}
		else if(strcmp(opt_channel, "-u")==0||strcmp(opt_channel, "--udp")==0)
		{
			// read ip addr from the command line...
			opt_channel_param_first = argv[3];//or set to a fixed value: e.g. "192.168.11.2"
			if (argc>4) opt_channel_param_second = strtoul(argv[4], NULL, 10);//e.g. "8089"
			opt_channel_type = CHANNEL_TYPE_UDP;
		}
		else
		{
			print_usage(argc, argv);
			return -1;
		}
	}
	else
	{
		print_usage(argc, argv);
        return -1;
	}

	if(opt_channel_type == CHANNEL_TYPE_SERIALPORT)
	{
		if (!opt_channel_param_first) {
#ifdef _WIN32
		// use default com port
		opt_channel_param_first = "\\\\.\\com3";
#elif __APPLE__
		opt_channel_param_first = "/dev/tty.SLAB_USBtoUART";
#else
		opt_channel_param_first = "/dev/ttyUSB0";
#endif
		}
	}

    
    // create the driver instance
	ILidarDriver * drv = *createLidarDriver();

    if (!drv) {
        fprintf(stderr, "insufficent memory, exit\n");
        exit(-2);
    }

    sl_lidar_response_device_info_t devinfo;
    bool connectSuccess = false;

    if(opt_channel_type == CHANNEL_TYPE_SERIALPORT){
        if(useArgcBaudrate){
            _channel = (*createSerialPortChannel(opt_channel_param_first, opt_channel_param_second));
            if (SL_IS_OK((drv)->connect(_channel))) {
                op_result = drv->getDeviceInfo(devinfo);

                if (SL_IS_OK(op_result)) 
                {
	                connectSuccess = true;
                }
                else{
                    delete drv;
					drv = NULL;
                }
            }
        }
        else{
            size_t baudRateArraySize = (sizeof(baudrateArray))/ (sizeof(baudrateArray[0]));
			for(size_t i = 0; i < baudRateArraySize; ++i)
			{
				_channel = (*createSerialPortChannel(opt_channel_param_first, baudrateArray[i]));
                if (SL_IS_OK((drv)->connect(_channel))) {
                    op_result = drv->getDeviceInfo(devinfo);

                    if (SL_IS_OK(op_result)) 
                    {
	                    connectSuccess = true;
                        break;
                    }
                    else{
                        delete drv;
					    drv = NULL;
                    }
                }
			}
        }
    }
    else if(opt_channel_type == CHANNEL_TYPE_UDP){
        _channel = *createUdpChannel(opt_channel_param_first, opt_channel_param_second);
        if (SL_IS_OK((drv)->connect(_channel))) {
            op_result = drv->getDeviceInfo(devinfo);

            if (SL_IS_OK(op_result)) 
            {
	            connectSuccess = true;
            }
            else{
                delete drv;
				drv = NULL;
            }
        }
    }


    if (!connectSuccess) {
        (opt_channel_type == CHANNEL_TYPE_SERIALPORT)?
			(fprintf(stderr, "Error, cannot bind to the specified serial port %s.\n"
				, opt_channel_param_first)):(fprintf(stderr, "Error, cannot connect to the specified ip addr %s.\n"
				, opt_channel_param_first));
		
        if(drv) {
            delete drv;
            drv = NULL;
        }
        return 0;
            
    }

    // print out the device serial number, firmware and hardware version number..
    printf("SLAMTEC LIDAR S/N: ");
    for (int pos = 0; pos < 16 ;++pos) {
        printf("%02X", devinfo.serialnum[pos]);
    }

    printf("\n"
            "Firmware Ver: %d.%02d\n"
            "Hardware Rev: %d\n"
            , devinfo.firmware_version>>8
            , devinfo.firmware_version & 0xFF
            , (int)devinfo.hardware_version);
    
            // Set up serial port for Arduino
    std::cout << "Enter the serial port for the Arduino and Baud Rate: ";
    std::string port;
    std::cin >> port;
    int baudRate;
    std::cin >> baudRate;
    float runTime = 0;
    std::cout << "How long do you want the program to run? (in seconds): " << std::endl;
    std::cin >> runTime;
    std::cout << "You entered: " << port << std::endl;
    std::cout << "The program will run for: " << runTime << " seconds." << "\n";
    std::cout << "Attempting to open " << port << "..." << std::endl;
    int fd;                             // File descriptor
    // Open port
    fd = open(port.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd == -1){
        printf("Device cannot be opened.\n");
        exit(-1);                       // If the device is not open, return -1
    }
    struct termios options;

    fcntl(fd, F_SETFL, FNDELAY);                    // Open the device in nonblocking mode

    // Set parameters
    tcgetattr(fd, &options);                        // Get the current options of the port
    bzero(&options, sizeof(options));               // Clear all the options
    speed_t         Speed;                         // Set the baud rate at 9600 bauds
    switch (baudRate)                               // Set the speed (baudRate)
    {
        case 110  :     Speed=B110; break;
        case 300  :     Speed=B300; break;
        case 600  :     Speed=B600; break;
        case 1200 :     Speed=B1200; break;
        case 2400 :     Speed=B2400; break;
        case 4800 :     Speed=B4800; break;
        case 9600 :     Speed=B9600; break;
        case 19200 :    Speed=B19200; break;
        case 38400 :    Speed=B38400; break;
        case 57600 :    Speed=B57600; break;
        case 115200 :   Speed=B115200; break;
        default : exit(-4);
    }
    cfsetispeed(&options, Speed);                   // Set the baud rate at 115200 bauds
    cfsetospeed(&options, Speed);
    options.c_cflag |= ( CLOCAL | CREAD |  CS8);    // Configure the device : 8 bits, no parity, no control
    options.c_iflag |= ( IGNPAR | IGNBRK );
    options.c_cc[VTIME]=0;                          // Timer unused
    options.c_cc[VMIN]=0;                           // At least on character before satisfy reading
    tcsetattr(fd, TCSANOW, &options);               // Activate the settings

    if (fd < 0)
        return 1;

    // check health...
    if (!checkSLAMTECLIDARHealth(drv)) {
        if(drv) {
            delete drv;
            drv = NULL;
        }
        return 0;
    }

    signal(SIGINT, ctrlc);
    
	if(opt_channel_type == CHANNEL_TYPE_SERIALPORT)
        drv->setMotorSpeed();
    // start scan...
    drv->startScan(0,1);

     // Open file for writing
    fout.open("/Users/mickelpickle/Documents/GitHub/MRL-Project/rplidar_sdk/points.csv", std::ios::out | std::ios::app);

    if (!fout.is_open()) {
        fprintf(stderr, "Failed to open points.csv for writing");
        return -1;
    }
    fout << "timestamp,angle,distance,R_x,R_y,R_z" << "\n";
    fout.flush(); // Ensure header is written

    auto start = std::chrono::high_resolution_clock::now();
    
    // fetech result and print it out...
    while (1) {
        sl_lidar_response_measurement_node_hq_t nodes[8192];
        size_t count = _countof(nodes);
        hasNewData = false;
        
        // Read serial data in non-blocking way
        char buffer[100];
        int n = read(fd, buffer, sizeof(buffer));
        if (n > 0) {
            std::lock_guard<std::mutex> lock(serial_mutex);
            current_serial_data = std::string(buffer, n);
            if (current_serial_data != lastSerialData) {
                hasNewData = true;
                lastSerialData = current_serial_data;
                storeIMUData(current_serial_data);
            }
        }
        storeIMUData(current_serial_data);
        // Get LIDAR data
        op_result = drv->grabScanDataHq(nodes, count);
        if (hasNewData) {
            if (SL_IS_OK(op_result)) {
                drv->ascendScanData(nodes, count);
                auto now = std::chrono::high_resolution_clock::now();
                // Compute the elapsed time in seconds
                double elapsed_seconds = std::chrono::duration<double>(now - start).count();
                if (elapsed_seconds >= runTime) {
                    std::cout << "\nProgram completed after " << elapsed_seconds << " seconds" << std::endl;
                    break; // Exit the loop after the specified time
                }
                // Display the elapsed time
                std::cout << "Seconds since start: " << elapsed_seconds << "s\r";
                std::cout.flush();

                for (int pos = 0; pos < (int)count; ++pos) {
                    float angle = (nodes[pos].angle_z_q14 * 90.f) / 16384.f;
                    float distance = nodes[pos].dist_mm_q2 / 4.0f;
                    int quality = nodes[pos].quality >> SL_LIDAR_RESP_MEASUREMENT_QUALITY_SHIFT;
                    
                    if (quality > 0) {
                        writeLidarData(angle, distance);
                    }
                }
            }
        } else {
            usleep(1000);
        }
        

        if (ctrl_c_pressed) {
            should_run = false;
            break;
        }
    }


    drv->stop();
    fout.close();
    close(fd);
	delay(200);
	if(opt_channel_type == CHANNEL_TYPE_SERIALPORT)
        drv->setMotorSpeed(0);
    // done!
}

