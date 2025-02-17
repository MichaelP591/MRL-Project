import asyncio
import serial
from rplidar import RPLidar
import csv
import pandas as pd
import numpy as np

# Configuration
SERIAL_INPUT_PORT = '/dev/tty.usbmodem101'  # Replace with your input serial port
INPUT_BAUD_RATE = 9600
BAUD_RATE: int = 115200
TIMEOUT: int = 0.25
DEVICE_PATH: str = '/dev/tty.usbserial-0001'
CSV_FILE = 'points.csv'

def verify_device() -> bool:
    from os import path
    return path.exists(DEVICE_PATH) and path.exists(SERIAL_INPUT_PORT)

async def read_serial_data(ser):
    while True:
        try:
            if ser.in_waiting > 0:
                line = int(ser.readline().strip())
                yield line
        except Exception as e:
            print(f"Serial error: {e}")
            break

async def lidar_scan(lidar, serial_gen, csv_writer):
    try:
        print("Starting RPLidar scan...")
        for scan in lidar.iter_scans():
            try:
                # Fetch the latest serial data
                servo_angle = await serial_gen.__anext__()

                print(f"Servo angle: {servo_angle}")
                print(f"Processing {len(scan)} measurements...")

                # Process lidar data
                offsets = np.array([(np.radians(meas[1]), meas[2]) for meas in scan if len(meas) >= 3])
                servoarray = np.full((len(offsets), 1), servo_angle)
                merged_data = np.hstack((offsets, servoarray))

                # Write to CSV
                csv_writer.writerows(merged_data)

            except StopIteration:
                print("No more serial data.")
                break
            except Exception as e:
                print(f"Lidar exception during scan: {e}")
                lidar.stop()
                lidar.clean_input()
                await asyncio.sleep(1)  # Pause before retrying
                continue

    except KeyboardInterrupt:
        print("Lidar scanning interrupted.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Stopping RPLidar...")
        lidar.stop()
        lidar.disconnect()

async def main():
    if not verify_device():
        print(f"Device not found: {DEVICE_PATH} or {SERIAL_INPUT_PORT}")
        return

    # Initialize serial and lidar
    ser = serial.Serial(SERIAL_INPUT_PORT, INPUT_BAUD_RATE, timeout=1)
    lidar = RPLidar(port=DEVICE_PATH, baudrate=BAUD_RATE, timeout=TIMEOUT)

    # Open CSV file for writing
    with open(CSV_FILE, mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['angle', 'distance', 'servo'])  # Header
        
        # Create an asynchronous generator for serial data
        serial_gen = read_serial_data(ser)

        # Run the lidar scan and merge data
        await lidar_scan(lidar, serial_gen, csv_writer)
    
    ser.close()
    print("Program finished.")

if __name__ == '__main__':
    asyncio.run(main())
