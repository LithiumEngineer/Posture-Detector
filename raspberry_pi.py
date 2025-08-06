from flask import Flask
from gpiozero import Servo
import threading
import time 

app = Flask(__name__)

servo = Servo(15) # GPIO 15 is the Servo port number 

motor_enabled = False

def motor():
    global motor_enabled
    while True:
        if motor_enabled:
            servo.max()
            time.sleep(0.2)
            
            servo.min()
            time.sleep(0.2)
        else:
            time.sleep(0.2)
            
@app.route('/spin_motor', methods=['POST'])
def spin_motor():
    global motor_enabled
    motor_enabled = True
    return "Motor ON", 200

@app.route('/stop_motor', methods=['POST'])
def stop_motor():
    global motor_enabled
    motor_enabled = False
    return "Motor OFF", 200

if __name__ == '__main__':
    thread = threading.Thread(target=motor_control_loop, daemon=True)
    thread.start()
    app.run(host='0.0.0.0', port=5000)
