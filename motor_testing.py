import requests
import time

def spin_motor():
    try:
        r = requests.post("http://192.168.0.139:5000/spin_motor", timeout=5)
        print("Spin motor response:", r.text)
    except requests.exceptions.RequestException as e:
        print("Spin motor request failed:", e)

def stop_motor():
    try:
        r = requests.post("http://192.168.0.139:5000/stop_motor", timeout=5)
        print("Stop motor response:", r.text)
    except requests.exceptions.RequestException as e:
        print("Stop motor request failed:", e)

spin_motor()

time.sleep(2) 

stop_motor()

time.sleep(2)

spin_motor()


