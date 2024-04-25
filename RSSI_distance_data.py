import paramiko
import getpass
import traceback
import threading

def execute_remote_command(ssh, command):
    """Execute a command on the remote server and print its output."""
    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.read().decode())

# hostname = "192.168.68.148"
# username = "ethan"
# hostname = "192.168.68.149"
# username = "pi"


def get_RSSI(hostname, username, password, num_threads):

    port = 22
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the server
        ssh.connect(hostname, port, username, password)
        
        # Create an SFTP session for file transfer
        # sftp = ssh.open_sftp()
        
        # Transfer the Python file to the Raspberry Pi
        # transfer_file(sftp, local_python_file, remote_python_file)
        
        # Execute the transferred Python file
        print((username + "'s execution ").ljust(32, "=")) 
        # command = f'python3 BLE-based-IPS/inquiry-with-RSSI.py 1'
        # threads = []

        # for i in range(num_threads):
            
        #     thread = threading.Thread(target=execute_remote_command, args=(ssh, command))
        #     #thread.daemon = True
        #     threads.append(thread)

        # for i in range(num_threads):
        #     threads[i].start()

        # for i in range(num_threads):
        #     threads[i].join()

        execute_remote_command(ssh, f'python3 BLE-based-IPS/inquiry-with-RSSI.py 1')

    except Exception as e:
        print(f"*** Caught exception: {e.__class__}: {e}")
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            #sftp.close()
            ssh.close()
        except:
            pass

if __name__ == "__main__":
    hostname = "192.168.68.135"
    username = "ethan"

    password = getpass.getpass(f"{username}@{hostname}'s password: ")
    get_RSSI(hostname, username, password, 2)