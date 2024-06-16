import subprocess
import tempfile
import time

processes = []

repetitions = 2
for i in range(repetitions):
    f = tempfile.TemporaryFile()
    p = subprocess.Popen(["python3", "inquiry-with-RSSI.py"], stdout=f)
    time.sleep(1)
    processes.append((p,f))

for p, f in processes:
    p.wait()
    f.seek(0)
    print(f.read())
    f.close()

