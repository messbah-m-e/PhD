# In the name of God

from tools.sim_tools import SimConnector
from tools.simple_flight import SimpleFlight
from tools.credentials import robot_id, password
import cv2
import time
sim = SimConnector(robot_id, password, is_local=False)
SimpleFlight(sim)
sim.reset()
# sim.set_main_cam_pose(0,-25,0)
sim.teleport_to_position(-304,-38,-12,0,0,90)
array = [(-304,-30,-2),
         (-304,-32,-2.54),
         (-304,-28,-2.68),
         (-302,-28,-3),
         (-306,-28,-3.5),
         (-301,-32,-6),
         (-315,-30,-4),
         (-284,-24,-5),
         (-310,-28,-11),
         (-282,-32,-10)]
for i in array:
    sim.move_to_position(i[0]+15,i[1]-15,i[2]-12,4,2)
    time.sleep(10)
    frame = sim.get_cam_image()[0][:,:,::-1]
    cv2.imwrite(f'{i[0]+15}_{i[1]-15,i[2]-12}.png',frame)
print('Hi - I am %s' % robot_id)
print('You can fly me with the following key combinations:')
print('Arrow keys: Up: Move forward, Down: Backward')
print('Arrow keys: Right: Rotate CW, Left: CCW')
print('PgUp: Move upward, PgDown: Downward')
print('Home: Go home, End: Immediate stop')
print('Space: Save snapshot, Esc: Quit')
print('You can also control me with other key combination or other logics')
print('For example you may want to control me not in the body frame but,')
print('in the world frame. This can be done using other provided flight')
print('functions in SimConnector class.')
