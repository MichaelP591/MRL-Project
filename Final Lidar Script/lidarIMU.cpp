#include <rplidar.h>

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

#include <mutex>
#include <atomic>
