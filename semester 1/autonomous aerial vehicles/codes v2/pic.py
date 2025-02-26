# In the name of God

import time
from tools.sim_tools import SimConnector
from tools.viewer import LiveViewer
from tools.credentials import robot_id, password


import numpy as np
import cv2

def save_image(counter):
    # print(f"saving image ... {counter}")
    # sim.immediate_stop()
    time.sleep(5.1)
    img1, img2, ts1, ts2, x1, y1, z1, qx1, qy1, qz1, qw1, x2, y2, z2, qx2, qy2, qz2, qw2 = sim.get_joint_image()
    drone_state = sim.get_drone_state()

    # time.sleep(.1)
    x,y,z = drone_state["position"]
    ox,oy,oz = drone_state["orientation"].as_euler('zyx', 
                                              degrees=True)

    cv2.imwrite(f'final/{counter}_{x:.2f}_{y:.2f}_{z:.2f}_{ox:.2f}_{oy:.2f}_{oz:.2f}_rgb.png', 
                img1)
    cv2.imwrite(f'final/{counter}_{x:.2f}_{y:.2f}_{z:.2f}_{ox:.2f}_{oy:.2f}_{oz:.2f}_depth.png', 
                img2)

    return None


sim = SimConnector(robot_id, password, is_local=False)
viewer = LiveViewer(sim, 5, show_osd=True)
viewer.start_view(with_depth=False)

epsilon = 0.1  # seconds

sim.reset()

counter = 2000

x = [40, 130]
y = [25, 100]
z = -5
# sim.teleport_to_position(x[0],#x
#                          y[0],#y
#                          z,#z
#                          0,#roll
#                          0,#pitch 
#                          0#yaw
#                          )
x = 180
sim.teleport_to_position(x,#x
                         -130,#y
                         z,#z
                         0,#roll
                         0,#pitch 
                         90#yaw
                         )
time.sleep(.5)
next_position = x,130, z

while viewer.is_live:
    if not viewer.is_live:
        break

    sim.move_to_position(next_position[0], 
                        next_position[1], 
                        next_position[2],
                        5,
                        3)
    save_image(counter)
    counter += 1
        
    depth_image = sim.get_depth_image()[0]
    depth_image = np.ravel(np.array(depth_image)[269:469, 100:, 0])
    if min(depth_image)<3:
        print("object near .... Going Up")
        sim.immediate_stop()
        time.sleep(.1)

        sim.move_by_body_vels(0,0,-2,.5)
        time.sleep(0.6)
    print()
    if min(depth_image)>30:
        print("no object near .... Going Down")


        sim.immediate_stop()
        time.sleep(.1)
        sim.move_by_body_vels(0,0,2,.5)
        time.sleep(0.6)
    print("-" *100)















