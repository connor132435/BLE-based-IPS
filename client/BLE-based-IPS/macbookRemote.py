import paramiko
import getpass
import sys
import traceback

def execute_remote_command(ssh, command):
    """Execute a command on the remote server and print its output."""
    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.read().decode())

def transfer_file(sftp, local_path, remote_path):
    """Transfer a file from the local machine to the remote server."""
    sftp.put(local_path, remote_path)
    print(f"Transferred {local_path} to {remote_path}")

# setup logging for debugging
paramiko.util.log_to_file("execution_demo.log")

# Server configuration
#hostname = "192.168.6.35"
#port = 22
#username = "ethan" or getpass.getuser()

# Local and remote paths for the Python file
# local_python_file = '/Users/ethansie/GoogleMentorship/BLE-based-IPS/inquiry-with-RSSI.py'
# remote_python_file = '/home/pi/BLE-based-IPE/inquiry-with-RSSI.py'  # Adjust the path as needed

# Create SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh_parameters = [
    {"hostname": "192.168.6.35",
     "username": "ethan",
        },
    {"hostname": "192.168.6.112",
     "username": "pi",
        }
    ]

for thing in ssh_parameters:
    port = 22
    hostname = thing["hostname"]
    username = thing["username"]
    password = getpass.getpass(prompt=f'{hostname}\'s password')
    try:
        # Connect to the server
        ssh.connect(hostname, port, username, password)
        
        # Create an SFTP session for file transfer
        # sftp = ssh.open_sftp()
        
        # Transfer the Python file to the Raspberry Pi
        # transfer_file(sftp, local_python_file, remote_python_file)
        
        # Execute the transferred Python file
        print((username + "'s execution ").ljust(32, "=")) 
        execute_remote_command(ssh, f'python3 BLE-based-IPS/inquiry-with-RSSI.py')

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
