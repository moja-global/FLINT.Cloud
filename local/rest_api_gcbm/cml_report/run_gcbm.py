import os
import requests
from threading import Timer
import time
import json

HOME = "http://localhost:8080/gcbm"
DONE = False

def run_gcbm():
    url = f"{HOME}/dynamic"
    req_data = {"title":"run4"}
    res = requests.post(url,data=req_data)
    return res.text

def status():
    url = f"{HOME}/status"
    req_data = {"title":"run4"}
    res = requests.post(url,data=req_data)
    return json.loads(res.text)



def display():
    global DONE
    sim_status = status()
    if sim_status['finished'] == 'In Progress':
        print(os.system("docker logs gcbm-api --until=30s"))
    else:
        DONE = True

class CheckSimulation(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args,**self.kwargs)
        print('Threading Done')

run_sim = run_gcbm()
print(run_sim)

timer = CheckSimulation(30,display)
timer.start()
print("Starting simulation")
time.sleep(300)
if not DONE:
    time.sleep(300)
timer.cancel()
