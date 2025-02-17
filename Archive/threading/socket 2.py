import socket
HOST = '127.0.0.1'  # Server IP (localhost for testing)
PORT = 12345        # Must match the C++ program's port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Connected!")

    while True:
        data = s.recv(1024).decode('utf-8')  # Adjust buffer size if needed
        if not data:
            break
        for line in data.splitlines():  
            print(data)  # Replace with your processing logic