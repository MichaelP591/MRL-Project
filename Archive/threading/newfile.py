import threading
import time
from rplidar import RPLidar
import serial
import pynmea2

# Shared data
shared_data = {
    "lidar": None,
    "servo": None,
    "timestamp": None
}
lock = threading.Lock()

# Sensor ports
LIDAR_PORT = "/dev/tty.usbserial-0001"
SERVO_PORT = "/dev/tty.usbmodem101"

# Lidar thread
def read_lidar():
    lidar = RPLidar(LIDAR_PORT)
    try:
        for scan in lidar.iter_scans():
            with lock:
                shared_data["lidar"] = scan
                shared_data["timestamp"] = time.time()
    except KeyboardInterrupt:
        print("Lidar thread stopping...")
    finally:
        lidar.stop()
        lidar.disconnect()

# GPS thread
def read_servo():
    with serial.Serial(SERVO_PORT, 9600, timeout=1) as servo_serial:
        while True:
            try:
                line = servo_serial.readline().strip()
                with lock:
                    shared_data["servo"] = (line)
                    shared_data["timestamp"] = time.time()
            except pynmea2.ParseError as e:
                print(f"Servo parse error: {e}")

# Data processing thread
def process_data():
    while True:
        with lock:
            lidar = shared_data.get("lidar")
            servo = shared_data.get("servo")
            timestamp = shared_data.get("timestamp")

        if lidar and servo:
            # Example: Combine and process the data
            print(f"Timestamp: {timestamp}")
            print(f"Lidar: {lidar[:5]}")  # Print first 5 lidar points
            print(f"Servo: {servo}")
            time.sleep(0.5)

# Start threads
threads = [
    threading.Thread(target=read_lidar, daemon=True),
    threading.Thread(target=read_servo, daemon=True),
    threading.Thread(target=process_data, daemon=True)
]

for thread in threads:
    thread.start()

# Keep main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping all threads...")
