import subprocess

processes = []

repetitions = 2
for i in range(repetitions):
    
    p = subprocess.Popen(["python3", "inquiry_with_with_rssi.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    processes.append(p)

for p in processes:
    p.wait()
    
    output, errors = p.commmunicate()
    print(output)
    
    