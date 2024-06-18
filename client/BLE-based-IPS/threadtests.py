import socket
import os
import threading
import time
import math
import requests
import argparse
import numpy as np

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

def parse():
    parser = argparse.ArgumentParser(description="Process some parameters.")

    # Adding the IP port argument
    parser.add_argument('--ip_port', type=str, required=True, help='IP port number')
    
    # Adding the ID number argument
    parser.add_argument('--id', type=int, required=True, help='ID number')
    
    parser.add_argument('--target_mac', type=str, required=True, help='Target MAC address')

    args = parser.parse_args()
    
    # Access the arguments
    ip_port = args.ip_port
    id_number = args.id
    target_mac = args.target_mac
    
    #print(f"IP Port: {ip_port}")
    #print(f"ID Number: {id_number}")

    return ip_port, id_number, target_mac

buffer = ''

server_ip_port, id_num, target_mac = parse()
#headphone_MAC = "94:DB:56:02:E2:46"
#desktop_ip = "192.168.68.151:8080"

rssi_history = []
max_history_length = 50

# Parameters for RSSI to distance conversion
# A = -59  # RSSI value at 1 meter
# n = 2.5    # Path-loss exponent

pi_locations = {1: [0.910, -0.910, 0.333], 
                2 : [0.450, 0.490, -0.350], 
                3 : [-0.846, 0.407, 0.050], 
                4 : [-0.900, -0.900, -0.500]}

dists = {1:[],2:[],3:[],4:[]}

pi1_mac = "DC:A6:32:39:46:FD"
pi2_mac = "AA:AA:AA:AA:AA:AA"
pi3_mac = "DC:A6:32:39:44:ED"
pi4_mac = "DC:A6:32:39:46:91"

def anchor_regression(distances, rssi_vals):
    logdata = [10* math.log10(dist) for dist in distances]
    rssi_neg = [-1* i for i in rssi_vals]
    ones = np.ones(len(distances), dtype= float)
    negones = [-1 * i for i in ones]
    M = np.array([logdata, negones])
    try:
        N = np.linalg.solve(M, rssi_neg)
    except:
        K = np.linalg.pinv(M)
        N = K @ rssi_neg

    return N[0], N[1]

for key in pi_locations.keys():
  for other_key in pi_locations.keys():

    loc = pi_locations[key]
    loc2 = pi_locations[other_key]

    a = loc[0] - loc2[0]
    b = loc[1] - loc2[1]
    c = loc[2] - loc2[2] 

    d = (a**2 + b**2 + c**2)**(0.5)

    dists[key].append(d * 39.3701 / 78)

last_rssi = [0,0,0,0]


def calc_A_n():
    cur_A = None
    cur_n = None
    dis = []
    ris = []

    for i in range(len(last_rssi)):
        if last_rssi != 0:
            dis.append(dists[i + 1])
            ris.append(last_rssi[i + 1])
    
    if (len(dis) == 0):
        return 2.9, -60
    cur_n, cur_A = anchor_regression(dis, ris)
    return cur_n, cur_A

# distances is dist from pi4 to pi1,pi2,pi3
# dame for rssi
# both 1d lists



# Lock to synchronize access to rssi_history
rssi_lock = threading.Lock()

def rssi_to_distance(rssi):
    n, A = calc_A_n()
    print(n, A)
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
                if target_mac in line:
                    args = line.split(" ")
                    rssi_history.append(int(args[2]))
                    if len(rssi_history) > max_history_length:
                        rssi_history.pop(0)

                if pi1_mac in line:
                    args = line.split(" ")
                    last_rssi[0] = int(args[2])
                
                if pi1_mac in line:
                    args = line.split(" ")
                    last_rssi[1] = int(args[2])
                
                if pi1_mac in line:
                    args = line.split(" ")
                    last_rssi[2] = int(args[2])
                
                if pi1_mac in line:
                    args = line.split(" ")
                    last_rssi[3] = int(args[2])

                

def calculate_and_print():
    while True:
        time.sleep(1)
        with rssi_lock:
            if len(rssi_history) > 0:
                distances = [rssi_to_distance(rssi) for rssi in rssi_history]
                avg_distance = sum(distances) / len(distances)
                print(sum(rssi_history)/ len(rssi_history))
                print(f"last {len(rssi_history)} avg distance: {avg_distance:.2f} meters")
                send_http_request(avg_distance)

# Function to send HTTP request with the last 25 RSSI values
def send_http_request(data):
    url = 'http://' + server_ip_port + "/reportBLE"  # Replace with your server URL
    payload = {
            'rssi_values': data,
            'ID': id_num
            }
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
