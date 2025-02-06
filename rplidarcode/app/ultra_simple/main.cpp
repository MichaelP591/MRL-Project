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
#include "./sdk/include/sl_lidar.h" 
#include "./sdk/include/sl_lidar_driver.h"

#include <mutex>
#include <atomic>

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
    }
    if (ms!=0)
        usleep(ms*1000);
}
#endif

using namespace sl;
using namespace std;

void handle_timeout(int sig) {
    cerr << "\nTimeout while attempting to open port." << endl;
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
            drv->reset();
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

// Add before main loop
std::string current_serial_data = "0";
std::mutex serial_mutex;
std::atomic<bool> should_run{true};
//main function
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
    cout << "Enter the serial port for the Arduino and Baud Rate: ";
    string port;
    cin >> port;
    int baudRate;
    cin >> baudRate;
    cout << "You entered: " << port << endl;
    cout << "Attempting to open " << port << "..." << endl;

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

    fstream fout;

    // Open file for writing
    fout.open("/Users/mickelpickle/Documents/GitHub/MRL-Project/points.csv", ios::out | ios::app);

    if (!fout.is_open()) {
        fprintf(stderr, "Failed to open points3d.csv for writing");
        return -1;
    }
    fout << "timestamp,angle,distance,servo" << "\n";
    fout.flush(); // Ensure header is written

    // Replace while loop with:
    while (should_run) {
        sl_lidar_response_measurement_node_hq_t nodes[8192];
        size_t count = _countof(nodes);
        
        // Read serial data in non-blocking way
        char buffer[100];
        int n = read(fd, buffer, sizeof(buffer));
        if (n > 0) {
            std::lock_guard<std::mutex> lock(serial_mutex);
            current_serial_data = std::string(buffer, n);
            //cout << "Serial data updated: " << current_serial_data << endl;
        }

        // Get LIDAR data
        op_result = drv->grabScanDataHq(nodes, count);
        if (SL_IS_OK(op_result)) {
            drv->ascendScanData(nodes, count);
            
            for (int pos = 0; pos < (int)count; ++pos) {
                float angle = (nodes[pos].angle_z_q14 * 90.f) / 16384.f;
                float distance = nodes[pos].dist_mm_q2 / 4.0f;
                int quality = nodes[pos].quality >> SL_LIDAR_RESP_MEASUREMENT_QUALITY_SHIFT;
                
                if (quality > 0) {
                    auto now = std::chrono::system_clock::now();
                    auto time_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                        now.time_since_epoch()).count();
                    
                    // Thread-safe read of serial data
                    std::string current_reading;
                    {
                        std::lock_guard<std::mutex> lock(serial_mutex);
                        current_reading = current_serial_data;
                    }
                    
                    // Write to CSV with proper formatting
                    fout << time_ms << "," << angle << "," << distance << "," << current_reading;
                    
                    //printf("%s theta: %03.2f Dist: %08.2f Q: %d time: %llu Serial: %s\n", 
                    //(nodes[pos].flag & SL_LIDAR_RESP_HQ_FLAG_SYNCBIT) ? "S " : "  ", angle, distance, quality, time_ms, current_reading.c_str());
                }
            }
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
