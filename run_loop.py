import time
import subprocess

INTERVAL_HOURS = 5  

while True:
    subprocess.run(["python", "Main.py"])
    time.sleep(INTERVAL_HOURS * 3600)
