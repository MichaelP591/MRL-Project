import csv
import serial
import threading
from rplidar import RPLidar
import time

# Configuration
LIDAR_PORT = '/dev/tty.usbserial-0001'  # Update with your RPLIDAR's port
SERIAL_PORT = '/dev/tty.usbmodem11101'   # Update with your serial device's port
BAUD_RATE = 9600           # Baud rate for the serial port
CSV_FILENAME = 'points.csv'

# Initialize shared variable and lock for thread-safe access
serial_data = None
lock = threading.Lock()

def read_serial():
    """Reads data from the serial port and updates the shared variable."""
    global serial_data
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1) as ser:
            while True:
                line = ser.readline().decode('utf-8').strip()
                with lock:
                    serial_data = line
    except serial.SerialException as e:
        print(f"Error reading serial port: {e}")

def read_lidar():
    """Reads data from the RPLIDAR and saves it to a CSV file."""
    lidar = RPLidar(LIDAR_PORT)
    try:
        with open(CSV_FILENAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Angle', 'Distance', 'Quality', 'Serial Data'])

            for measurement in lidar.iter_measurments():
                quality, angle, distance = measurement[0], measurement[2], measurement[3]
                timestamp = time.time()

                with lock:
                    current_serial_data = serial_data

                # Write the data to the CSV file
                writer.writerow([timestamp, angle, distance, quality, current_serial_data])
                print(f"LIDAR: Angle={angle}, Distance={distance}, Quality={quality}, Serial={current_serial_data}")
    except KeyboardInterrupt:
        print("Stopping LIDAR...")
    finally:
        lidar.stop()
        lidar.disconnect()

# Start the serial reading thread
serial_thread = threading.Thread(target=read_serial, daemon=True)
serial_thread.start()

# Start reading from the LIDAR
read_lidar()
