"""
Run the whole simulation
"""

import os
from urllib.request import Request
import requests
import json

HOME = "http://0.0.0.0:8080/gcbm"
RESPONSES = []

def run_simulation():
    url = f"{HOME}/dynamic"
    req_data = {"title":"run4"}
    res = requests.post(url,data=req_data)
    return res

def get_status():
    url = f"{HOME}/status"
    req_data = {"title":"run4"}
    res = requests.post(url,data=req_data)
    return res.text

if __name__ == "__main__":
    run_sim = run_simulation()
    status = get_status()
    while(status == {'finished':'In Progress'}):
        status = get_status()
