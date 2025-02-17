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
#include "/Users/mickelpickle/Documents/GitHub/MRL-Project/sdk/include/sl_lidar.h" 
#include "/Users/mickelpickle/Documents/GitHub/MRL-Project/sdk/include/sl_lidar_driver.h"
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

    std::cout << "Closest IMU Reading: [" << std::get<1>(closest) << "]" << std::endl;
    return std::get<1>(closest);
}


void writeLidarData(int angle, int distance) {
    
    auto now = std::chrono::system_clock::now();
    int64_t lidar_time_ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();

    std::string imu_reading = getClosestIMUReading(lidar_time_ms);
    
    fout << lidar_time_ms << "," << angle << "," << distance << "," << imu_reading << std::endl;
}

//main function
int main() {
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

    std::string lidarSerialPort = "";
    std::cout << "This program gathers data for Slamtech LIDAR and writes the data to points.csv" << "\n" 
              << "Enter the serial port for the Slamtech LIDAR";
    std::cin >> lidarSerialPort;
    cout << "You entered: " << lidarSerialPort << endl;

    opt_channel_param_first = lidarSerialPort.c_str();
    opt_channel_param_second = 115200;
    
    // create the driver instance
	ILidarDriver * drv = *createLidarDriver();

    if (!drv) {
        fprintf(stderr, "insufficent memory, exit\n");
        exit(-2);
    }

    sl_lidar_response_device_info_t devinfo;
    bool connectSuccess = false;

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

    // Open file for writing
    fout.open("points.csv", ios::out | ios::app);

    if (!fout.is_open()) {
        fprintf(stderr, "Failed to open points.csv for writing");
        return -1;
    }
    fout << "timestamp,angle,distance,R_x,R_y,R_z" << "\n";
    fout.flush(); // Ensure header is written

    // This is the main loop that runs the data collection
    while (should_run) {
        sl_lidar_response_measurement_node_hq_t nodes[8192];
        size_t count = _countof(nodes);
        hasNewData = false;
        
        // Read serial data in non-blocking way
        char buffer[100];
        int n = read(fd, buffer, sizeof(buffer));
        if (n > 0) {
            lock_guard<std::mutex> lock(serial_mutex);
            current_serial_data = string(buffer, n);
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
