# In the name of God

import time
from tools.sim_tools import SimConnector
from tools.viewer import LiveViewer
from tools.credentials import robot_id, password


import pandas as pd
import numpy as np
import cv2
import utils
import json

calibration_data = utils.load_calibration_data("camera_calibration.npz")
detected_objects = []

# def detect_and_cordinate(counter):
    
#     imgs_data, drone_state = get_sim_data()

#     undistorted_img = utils.undistorted_imgs(imgs_data[0], calibration_data)
    
#     detections = utils.detect_objects(undistorted_img)

#     cam_rot, cam_pos = utils.get_camera_extrinsic(drone_state)
#     x,y,z = drone_state["position"]
#     ox,oy,oz = drone_state["orientation"].as_euler('zyx', 
#                                               degrees=True)
#     print(x,y,z,ox,oy,oz)
#     cv2.imwrite(f'D:\phd\\0 term 1\AAV\FinalProject\codes v2\qqw/rgb//{counter.counter}_{x:.2f}_{y:.2f}_{z:.2f}_{ox:.2f}_{oy:.2f}_{oz:.2f}_rgb.png', 
#                 imgs_data[0])
#     cv2.imwrite(f'D:\phd\\0 term 1\AAV\FinalProject\codes v2\qqw/dep//{counter.counter}_{x:.2f}_{y:.2f}_{z:.2f}_{ox:.2f}_{oy:.2f}_{oz:.2f}_depth.png', 
#                 imgs_data[1])

    
#     if len(detections) > 0:
#         try:
#             for det in detections:
#                 pos = utils.pixel_to_global(det['bbox'], imgs_data[1], cam_rot, cam_pos, calibration_data)
#                 cls = det['class']
#                 filter = utils.filter_detection(pos, cls, detected_objects)
#                 if not filter:
#                     detected_objects.append({
#                         'img_id': counter.counter,
#                         'class': det['class'], 
#                         'position': pos.tolist(), 
#                         'cam_pos': cam_pos.tolist(),
#                         'drone_pos': drone_state['position'],
#                         'dron_ori': drone_state['orientation'].as_quat().tolist(),
#                         'bbox': det['bbox']
#                     })

#         except ValueError as error:
#             print("Value error!!! ", error)
#     print(detected_objects)
#     with open("sample.json", "w") as outfile:
#         json.dump(detected_objects, outfile)


# def get_sim_data():
#     rgb_img, depth_img, depth_float, *_ = sim.get_joint_image()
#     drone_state = sim.get_drone_state()
    
#     imgs_data = [rgb_img, depth_float]
    
#     return imgs_data, drone_state


class Counter:
    def __init__(self):
        self.counter = 0

    def increment(self):
        self.counter += 1
        print(self.counter)

def get_depth():
    time.sleep(epsilon)
    depth_image = sim.get_joint_image()[2][:220,241:542]
    depth_image = np.ravel(depth_image)
    return min(depth_image)


def get_h():
    time.sleep(0.1)
    return sim.get_drone_state()["position"][2]

def save_image(counter):
    print(f"saving image ... {counter}")
    sim.immediate_stop()
    time.sleep(0.1)
    img1, img2, ts1, ts2, x1, y1, z1, qx1, qy1, qz1, qw1, x2, y2, z2, qx2, qy2, qz2, qw2 = sim.get_joint_image()
    drone_state = sim.get_drone_state()

    # time.sleep(.1)
    x,y,z = drone_state["position"]
    ox,oy,oz = drone_state["orientation"].as_euler('zyx', 
                                              degrees=True)

    cv2.imwrite(f'final/{counter.counter}_{x:.2f}_{y:.2f}_{z:.2f}_{ox:.2f}_{oy:.2f}_{oz:.2f}_rgb.png', 
                img1)
    cv2.imwrite(f'final/{counter.counter}_{x:.2f}_{y:.2f}_{z:.2f}_{ox:.2f}_{oy:.2f}_{oz:.2f}_depth.png', 
                img2)

    return None

def adjust_drone_height(target_height, duration=0.1, epsilon=0.1):
    h = get_h()
    direction = 0  # 1: Up, -1: Down, 0: No movement
    
    if h < target_height - 0.1:
        direction = 1
    elif h > target_height + 0.1:
        direction = -1
    
    if direction != 0:
        sim.move_by_body_vels(0, 0, direction, duration)
        time.sleep(duration + epsilon)

def take_pictures_from_both_sides(duration=3, epsilon=0.1):
    rotate_drone(270)
    # detect_and_cordinate(counter)
    counter.increment() 
    rotate_drone(90)
    # detect_and_cordinate(counter)
    counter.increment() 

def adjust_and_move_forward(target_height, speed=1, duration=1.5, epsilon=0.1):
    """
    Adjusts the drone's height and moves it forward until the depth condition is met.
    """
    depth = get_depth()
    while depth > 2.5:
        adjust_drone_height(target_height)
        sim.move_by_body_vels(speed, 0, 0, duration)
        time.sleep(duration + epsilon)
        depth = get_depth()
        # detect_and_cordinate(counter)
        counter.increment() 
        print(depth)

def rotate_drone(yaw, duration=3, epsilon=0.1):
    """
    Rotates the drone to a specified yaw angle.
    """
    time.sleep(epsilon)
    sim.rotate_to_yaw(yaw, duration, 0)
    time.sleep(duration + epsilon)

sim = SimConnector(robot_id, password, is_local=False)
viewer = LiveViewer(sim, 5, show_osd=True)
viewer.start_view(with_depth=False)
sim.reset()



epsilon = 0.1  # seconds
counter = Counter()


# x = [-215,-18.5,-5.2]
# x_out= [-215,-55,-6]
x = [-150,-15,-6]
x_out = [-150,-55,-6]

# next_position = x,y, z
movement = []


sim.teleport_to_position(x[0],x[1],x[2],0,0,270)
time.sleep(0.1)
drone_state = sim.get_drone_state()["position"]
movement.append(drone_state)

while viewer.is_live:
    if not viewer.is_live:
        break


    # 10 meter forward
    time.sleep(3)
    duration = 3.5
    sim.move_by_body_vels(2.5, 0, 0, duration)
    time.sleep(duration+1.1)
    take_pictures_from_both_sides()
    time.sleep(duration+1.1)
    drone_state = sim.get_drone_state()["position"]
    movement.append(drone_state)

    rotate_drone(180)
    adjust_and_move_forward(x[2])
    take_pictures_from_both_sides()
    time.sleep(duration+1.1)
    drone_state = sim.get_drone_state()["position"]
    movement.append(drone_state)

    # move to other side 
    rotate_drone(0)
    adjust_and_move_forward(x[2])
    take_pictures_from_both_sides()
    time.sleep(duration+1.1)
    drone_state = sim.get_drone_state()["position"]
    movement.append(drone_state)

    # look forward
    rotate_drone(270)
    # move to center
    drone_state = sim.get_drone_state()["position"]
    movement.append(drone_state)
    sim.move_to_position(x[0],drone_state[1],x[2],5,3)
    time.sleep(3+.1)
    adjust_drone_height(x[2])

    drone_state = sim.get_drone_state()["position"]
    print(drone_state)
    movement.append(drone_state)
    print("-" *100)




    if drone_state[1] < x_out[1] + 9:

        sim.immediate_stop()
        sim.move_to_position(x_out[0],x_out[1],x_out[2],2,4)
        time.sleep(4+.1)
        break


drone_state = sim.get_drone_state()["position"]
movement.append(drone_state)
print(len(movement))
# print(movement)
print("-" * 10)
DF = pd.DataFrame(movement) 
DF.to_csv("data.csv")






