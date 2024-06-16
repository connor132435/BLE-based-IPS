import socket
import os
import threading
import time
import math
import requests

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
desktop_ip = "192.168.68.141:8080"

rssi_history = []
max_history_length = 25

# Parameters for RSSI to distance conversion
A = -60  # RSSI value at 1 meter
n = 2    # Path-loss exponent

# Lock to synchronize access to rssi_history
rssi_lock = threading.Lock()

def rssi_to_distance(rssi):
    return 10 ** ((A - rssi) / (10 * n))

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
                distances = [rssi_to_distance(rssi) for rssi in rssi_history]
                avg_distance = sum(distances) / len(distances)
                print(f"last {len(rssi_history)} avg distance: {avg_distance:.2f} meters")
                send_http_request(avg_distance)

# Function to send HTTP request with the last 25 RSSI values
def send_http_request(data):
    url = 'http://' + desktop_ip + "/reportBLE"  # Replace with your server URL
    payload = {'rssi_values': data}
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Successfully sent data: {data}")
        else:
            print(f"Failed to send data, status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")


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
