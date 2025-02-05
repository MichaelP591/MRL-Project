import pygame
import serial
import serial.tools.list_ports
import numpy as np
from math import cos, sin, radians


def find_mpu6050_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"Found port: {port.device} - {port.description}")
        # If you know the VID/PID of your device, check like this:
        if "MPU" in port.description or "Arduino" in port.description:
            return port.device  # e.g., "COM3" on Windows or "/dev/ttyUSB0" on Linux
    return None

port = find_mpu6050_port()

if port:
    print(f"Using port: {port}")
else:
    print("MPU6050 not found!")

# Set up serial connection (update the port accordingly)
ser = serial.Serial(port, 115200)  # Change 'COM3' to your Arduino port

# Pygame setup
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('MPU6050 3D Visualization')
clock = pygame.time.Clock()

# 3D cube vertices
vertices = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                     [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]])

# Edges connecting the vertices
edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4),
         (0,4), (1,5), (2,6), (3,7)]

def read_mpu():
    """Reads roll, pitch & yaw from serial data"""
    try:
        line = ser.readline().decode('utf-8').strip()  # Read line from serial
        roll, pitch, yaw = map(float, line.split(','))  # Parse roll, pitch, yaw
        print(roll, pitch, yaw)
        return roll, pitch, yaw
    except:
        print("error ")
        return 0, 0, 0  # Default to no rotation if read fails

def rotate_3d(point, roll, pitch, yaw):
    """Applies 3D rotation to a point based on roll, pitch, yaw"""
    roll, pitch, yaw = radians(roll), radians(pitch), radians(yaw)
    
    # Rotation matrices
    R_x = np.array([[1, 0, 0],
                    [0, cos(roll), -sin(roll)],
                    [0, sin(roll), cos(roll)]])
    
    R_y = np.array([[cos(pitch), 0, sin(pitch)],
                    [0, 1, 0],
                    [-sin(pitch), 0, cos(pitch)]])
    
    R_z = np.array([[cos(yaw), -sin(yaw), 0],
                    [sin(yaw), cos(yaw), 0],
                    [0, 0, 1]])
    
    rotated_point = np.dot(point, R_z)
    rotated_point = np.dot(rotated_point, R_y)
    rotated_point = np.dot(rotated_point, R_x)
    return rotated_point

def project_point(point, width, height, scale=200):
    """Projects a 3D point onto 2D screen space"""
    x, y, z = point
    factor = scale / (z + 5)  # Perspective divide
    x, y = int(x * factor + width / 2), int(y * factor + height / 2)
    return (x, y)

running = True
while running:
    screen.fill((110, 196, 116))  # Background color
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    roll, pitch, yaw = read_mpu()
    
    # Rotate and project vertices
    transformed_vertices = [rotate_3d(v, roll, pitch, yaw) for v in vertices]
    projected_vertices = [project_point(v, width, height) for v in transformed_vertices]

    # Draw edges
    for edge in edges:
        pygame.draw.line(screen, (0, 150, 255), projected_vertices[edge[0]], projected_vertices[edge[1]], 2)
        
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
ser.close()
