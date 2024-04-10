import paramiko
import getpass
import traceback

def execute_remote_command(ssh, command):
    """Execute a command on the remote server and print its output."""
    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.read().decode())

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

port = 22
hostname = "192.168.68.132"
username = "ethan"
password = getpass.getpass(prompt=f"{hostname}\'s password => ")

ssh.connect(hostname, port, username, password)

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