import time
import subprocess

INTERVAL_HOURS = 5  

while True:
    subprocess.run(["python", "SteamPlayerCounter.py"])
    time.sleep(INTERVAL_HOURS * 3600)
