import socket
import os
import threading
import time
import csv

# Socket setup
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
headphone_MAC = "DC:A6:32:39:46:FD"

# Maximum number of readings to store in a column
max_readings = 50
readings_count = 0
current_column = 1  # Start from the first column (index 0 for csv writer)

# Lock to synchronize access to rssi_history
rssi_lock = threading.Lock()

# Initialize the CSV file
csv_file = 'rssi_readings.csv'

# Create a new CSV file and leave the first row blank
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([])  # Leave the first row blank

def receive_data():
    global buffer, readings_count, current_column
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
                    rssi = int(args[2])
                    if readings_count < max_readings:
                        # Append the RSSI value to the CSV file
                        with open(csv_file, mode='r+', newline='') as file:
                            reader = csv.reader(file)
                            rows = list(reader)
                            
                            # Ensure we have enough columns in the first row
                            if len(rows) == 0:
                                rows.append([])
                            while len(rows[0]) <= current_column:
                                rows[0].append('')
                            
                            # Ensure we have enough rows
                            while len(rows) <= readings_count + 1:
                                rows.append([''] * len(rows[0]))
                            
                            # Insert the RSSI value
                            rows[readings_count + 1][current_column] = rssi
                            
                            # Write back to the CSV
                            file.seek(0)
                            writer = csv.writer(file)
                            writer.writerows(rows)
                        
                        readings_count += 1
                        print(f"Logged RSSI: {rssi} at row {readings_count + 1}, column {current_column + 1}")
                        
                    else:
                        print("Reached maximum readings, waiting for user input to continue.")
                        return

def wait_for_user_input():
    input("Press Enter to continue adding new readings...")

# Create and start the thread
receive_thread = threading.Thread(target=receive_data, daemon=True)
receive_thread.start()

try:
    while True:
        if readings_count >= max_readings:
            wait_for_user_input()
            with rssi_lock:
                readings_count = 0  # Reset the readings count
                current_column += 1  # Move to the next column
            receive_thread = threading.Thread(target=receive_data, daemon=True)
            receive_thread.start()
        time.sleep(1)
except KeyboardInterrupt:
    print("Interrupted by user")
finally:
    connection.close()
    os.unlink(socket_path)