import socket
import os

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

try:
    while True:
        data = connection.recv(1024)
        string = data.decode()
        buffer += string

        lines = buffer.split("\n")
        buffer = lines.pop()

        for line in lines:
            if headphone_MAC in line:
                args = line.split(" ")
                rssi_history.append(int(args[2]))
        if (len(rssi_history) > max_history_length):
            rssi_history = rssi_history[-max_history_length:]
        avg = sum(rssi_history)/max_history_length
        print(f"last 25 avg: {avg}")

except KeyboardInterrupt:
    print("interrupt by user")
finally:
    connection.close()
    os.unlink(socket_path)

