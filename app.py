import tensorflow as tf
import numpy as np
from matplotlib import pyplot
import cv2
from constants import EDGES
import subprocess
import math
import time


last_bad = [-1, -1] # -1 = last recorded posture is good

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

def draw_points(frame, points, conf): 
    y, x, c = frame.shape
    shaped = np.multiply(points, [y, x, 1])
    
    for point in shaped[0][0]: 
        py, px, pc = point
        if pc > conf: 
            cv2.circle(frame, (int(px), int(py)), 5, (255, 0, 0), -1)

def draw_connections(frame, edges, points, conf): 
    y, x, c = frame.shape
    shaped = np.multiply(points, [y, x, 1])
    
    for i, (edge, desc) in enumerate(edges.items()):
        p1, p2 = edge
        y1, x1, c1 = shaped[0][0][p1]
        y2, x2, c2 = shaped[0][0][p2]
        if (c1 > conf) and (c2 > conf): # good posture = green, bad posture = red 
            if desc == "spine":  
                if calculate_angle([x1, y1], [x2, y2], [0, y2]) > 90:  
                    cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 4)
                    if(last_bad[i] != -1 and int(time.time()) - last_bad[i] >= 60):
                        spin_motor()
                        last_bad = -1
                    elif (last_bad[i] != -1 and int(time.time()) - last_bad[i] >= 30): 
                        send_notification("Check posture", "Spine") 
                        last_bad[i] = -1
                        
                    if (last_bad[i] == -1): 
                        last_bad[i] = int(time.time())
                else:
                    cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
                    last_bad[i] = -1
                    stop_motor()

def calculate_angle(a, b, c): 
    v1 = [a[0] - b[0], a[1] - b[1]]
    v2 = [c[0] - b[0], c[1] - b[1]]

    dot_product = v1[0] * v2[0] + v1[1] * v2[1] 
    magnitude_v1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    magnitude_v2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

    cos_angle = dot_product / (magnitude_v1 * magnitude_v2) 

    cos_angle = max(cos_angle, -1)
    cos_angle = min(cos_angle, 1)

    angle_rad = math.acos(cos_angle) 
    angle_deg = math.degrees(angle_rad)
    
    return angle_deg 


def check_posture(edges, points, conf): 
    print("Checking posture")

def send_notification(title, message):
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(['osascript', '-e', script])

def main(): 
    send_notification('Posture detection activated', 'You will now get real-time alerts to give you feedback on your posture.')
    interpreter = tf.lite.Interpreter(model_path='3.tflite')
    interpreter.allocate_tensors()
    video = cv2.VideoCapture(0)
    
    while video.isOpened(): 
        ret, frame = video.read()
        
        # Preprocessing image, reshaping into 192x192x3
        img = frame.copy()
        img = tf.expand_dims(img, axis=0)
        img = tf.image.resize_with_pad(img, 192, 192)
        input_image = tf.cast(img, dtype=tf.float32)

        # Retrieving points
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        interpreter.set_tensor(input_details[0]['index'], np.array(input_image))
        interpreter.invoke()

        points = interpreter.get_tensor(output_details[0]['index'])
        
        # drawing keypoints
        draw_connections(frame, EDGES, points, 0.4)
        draw_points(frame, points, 0.4)
        

        cv2.imshow('Window', frame)
    
        if cv2.waitKey(10) & 0xFF==ord('q'):
            break
    
    video.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
