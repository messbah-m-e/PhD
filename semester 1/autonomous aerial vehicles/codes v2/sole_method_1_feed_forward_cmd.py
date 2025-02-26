# In the name of God

import time
from tools.sim_tools import SimConnector
from tools.viewer import LiveViewer
from tools.credentials import robot_id, password

import utils

# from ultralytics import YOLO
import numpy as np
import cv2
from scipy.spatial.transform import Rotation as R

import numpy as np
import cv2
import pandas as pd 


class Counter:
    def __init__(self):
        self.counter = 0

    def increment(self):
        self.counter += 1
        # print(self.counter)

def left_to_right():
    duration = 3
    sim.rotate_yaw_rate(30, duration)
    time.sleep(duration+epsilon+1)

    save_image(counter.counter)
    counter.increment() 
    
    depth = get_depth()
    if depth >10:
        # move 10 meter
        duration = 5
        sim.move_by_body_vels(2, 0, 0, duration)
        time.sleep(duration+epsilon)
    elif 1<depth<=10:
        duration = (depth - .3)/2
        sim.move_by_body_vels(2, 0, 0, duration)
        time.sleep(duration+epsilon)

    print(f'move forward {duration*2} meters')

    duration = 3
    sim.rotate_yaw_rate(30, duration)
    time.sleep(duration+epsilon)

def right_to_left():
    duration = 3
    sim.rotate_yaw_rate(-30, duration)
    time.sleep(duration + epsilon)

    save_image(counter.counter)
    counter.increment() 

    depth = get_depth()
    if depth >10:
        # move 10 meter
        duration = 5
        sim.move_by_body_vels(2, 0, 0, duration)
        time.sleep(duration+epsilon)
    elif 2<depth<=10:
        duration = (depth - .3)/2
        sim.move_by_body_vels(2, 0, 0, duration)
        time.sleep(duration+epsilon)

    print(f'move forward {duration*2} meters')
    
    duration = 3
    sim.rotate_yaw_rate(-30, duration)
    time.sleep(duration + epsilon)

def get_depth():
    time.sleep(epsilon)
    depth_image = sim.get_joint_image()[2][:220,241:542]
    depth_image = np.ravel(depth_image)
    return min(depth_image)

def get_h():
    time.sleep(0.1)
    return sim.get_drone_state()["position"][2]

def save_image(counter):
    time.sleep(epsilon)
    imgs = sim.get_joint_image()
    drone_state = sim.get_drone_state()

    x,y,z = drone_state["position"]
    ox,oy,oz = drone_state["orientation"].as_euler('zyx', 
                                              degrees=True)

    cv2.imwrite(f'final/{counter}_{x:.2f}_{y:.2f}_{z:.2f}_{ox:.2f}_{oy:.2f}_{oz:.2f}_rgb.png', 
                imgs[0])
    cv2.imwrite(f'final/{counter}_{x:.2f}_{y:.2f}_{z:.2f}_{ox:.2f}_{oy:.2f}_{oz:.2f}_depth.png', 
                imgs[2])

    return None



sim = SimConnector(robot_id, password, is_local=False)
viewer = LiveViewer(sim, 5, show_osd=True)
viewer.start_view(with_depth=False)


sim.reset()

counter = Counter()

min_depth = 4.5
epsilon = 0.5


# ورودی
x = [-215,-15,-6]
# ورودی دومی
# x = [-150,-15,-6]
x_out= [-215,-55,-6]
sim.teleport_to_position(x[0],x[1],x[2],0,0,270)
time.sleep(epsilon)


movement = []


drone_state = sim.get_drone_state()["position"]
movement.append(drone_state)
# entering and rotate left toward wall 
duration = 6
sim.move_by_body_vels(2, 0, 0, duration)
time.sleep(duration+epsilon)
drone_state = sim.get_drone_state()["position"]
movement.append(drone_state)

duration = 3
print("Rotate -90 degrees toward wall")
sim.rotate_yaw_rate(-30, duration)
time.sleep(duration + epsilon)

drone_state = sim.get_drone_state()["position"]
movement.append(drone_state)
lr =0
while viewer.is_live:
    if not viewer.is_live:
        break

    save_image(counter.counter)
    counter.increment() 

    # Control altitude
    h = get_h()
    duration = 0.5
    direction = 0  
    if h < x[2] - 0.5:
        direction = 1
    elif h > x[2] + 0.5:
        direction = -1

    if direction != 0:
        sim.move_by_body_vels(0, 0, direction, duration)
        time.sleep(duration + epsilon)
        


    # detect_and_cordinate() 

    # Forward movement
    duration = 2
    sim.move_by_body_vels(1, 0, 0, duration)
    time.sleep(duration + epsilon)
    drone_state = sim.get_drone_state()["position"]
    movement.append(drone_state)

    # Depth check and turning
    depth = get_depth()
    if depth <= min_depth:
        print(depth)
        if lr == 0:
            print("left to right")
            left_to_right()
        else:
            print("right to left")
            right_to_left()
        lr = 1 - lr 
    # moving out

    # print(f'movement append')
    # print(drone_state[1], x_out[1]+5)
    if drone_state[1] < x_out[1]+8:
        sim.immediate_stop()
        sim.move_to_position(x_out[0],x_out[1],x_out[2],2,4)
        

drone_state = sim.get_drone_state()["position"]
movement.append(drone_state)
print(len(movement))
# print(movement)
print("-" * 10)
DF = pd.DataFrame(movement) 
DF.to_csv("data1.csv")
