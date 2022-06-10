"""
Run the whole simulation
"""

import os
import requests
import json
import threading
import logging

HOME = "http://localhost:8080/gcbm"

def run_simulation():
    url = f"{HOME}/dynamic"
    req_data = {"title":"run4"}
    start_req = requests.post(url,data=req_data)
    return start_req

def get_status():
    url = f"{HOME}/status"
    req_data = {"title":"run4"}
    res = requests.post(url,req_data)
    return json.loads(res.text)

def check_if_finished():
    status = get_status()
    t = threading.Timer(10.0,check_if_finished)
    if status['finished'] == 'In Progress':
        t.start()
        print(status['finished'])
    else:
        t.cancel()


if __name__ == "__main__":
    run_process = run_simulation()
    check_if_finished()
    
    
    
