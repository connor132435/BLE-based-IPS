import socket
import os
import threading
import time

socket_path = "/tmp/btlemon.sock"

try:
    os.unlink(socket_path)
except OSError:
    if os.path.exists(socket_path):
        raise

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(socket_path)
server.listen(1)

connection, client_address = server.accept()

buffer = ''
headphone_MAC = "94:DB:56:02:E2:46"

rssi_history = []
max_history_length = 25

# Lock to synchronize access to rssi_history
rssi_lock = threading.Lock()

def receive_data():
    global buffer
    while True:
        data = connection.recv(1024)
        if not data:
            break
        string = data.decode()
        buffer += string

        lines = buffer.split("\n")
        buffer = lines.pop()

        with rssi_lock:
            for line in lines:
                if headphone_MAC in line:
                    args = line.split(" ")
                    rssi_history.append(int(args[2]))
                    if len(rssi_history) > max_history_length:
                        rssi_history.pop(0)

def calculate_and_print():
    while True:
        time.sleep(1)
        with rssi_lock:
            if len(rssi_history) > 0:
                avg = sum(rssi_history) / len(rssi_history)
                print(f"last {len(rssi_history)} avg: {avg}")

# Create threads
receive_thread = threading.Thread(target=receive_data, daemon=True)
calculate_thread = threading.Thread(target=calculate_and_print, daemon=True)

# Start threads
receive_thread.start()
calculate_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("interrupt by user")
finally:
    connection.close()
    os.unlink(socket_path)