import numpy as np
from scipy.spatial.transform import Rotation as R
import cv2
from ultralytics import YOLO
import math

model = YOLO("yolo\\yolo11n.pt")

def load_calibration_data(calibration_file):
    calibration = np.load(calibration_file)
    calibration_data = {
        'camera_matrix': calibration['camera_matrix'],
        'dist_coeffs': calibration['dist_coeffs'],
        'rvecs': calibration['rvecs'],
        'tvecs': calibration['tvecs']
    }
    return calibration_data

def get_camera_extrinsic(drone_state):
    
    # drone position and orientation(NED)
    drone_pos = drone_state['position']
    drone_quat = drone_state['orientation'].as_quat()

    # Converting the drone's orientation into a rotation matrix
    drone_rot = R.from_quat(drone_quat).as_matrix()


    # Camera position relative to the drone (Body to Camera)
    cam_offset = np.array([0, 0, 0.24])

    R_cam_to_body = np.array([[0, 0, 1],
                              [1, 0, 0],
                              [0, 1, 0]])
    
    R_pitch = R.from_euler('x', -25, degrees=True).as_matrix()
    
    cam_rot_body = R_cam_to_body @ R_pitch
    
    # Becoming a global space
    cam_pos_world = drone_pos + drone_rot @ cam_offset
    cam_rot_world = drone_rot @ cam_rot_body
    
    return cam_rot_world, cam_pos_world

def undistorted_imgs(rgb_img, calibration_data):
    K = calibration_data['camera_matrix']
    D = calibration_data['dist_coeffs']

    # For RGB: Use undistort with default bilinear interpolation
    undistorted_rgb = cv2.undistort(rgb_img, K, D, None, K)

    return undistorted_rgb

def pixel_to_global(bbox, depth_img, cam_rot, cam_pos, calibration_data):
    
    x_min, y_min, x_max, y_max = bbox
    # Image distortion correction
    u_center = int((x_min + x_max) / 2)
    v_center = int((y_min + y_max) / 2)
    
    # u_corrected, v_corrected = pts[0][0]

    fx = calibration_data['camera_matrix'][0, 0]
    fy = calibration_data['camera_matrix'][1, 1]
    cx = calibration_data['camera_matrix'][0, 2]
    cy = calibration_data['camera_matrix'][1, 2]

    # Calculating the ray direction in camera coordinates
    z_roi = depth_img[int(v_center)-2:int(v_center)+2, int(u_center)-2:int(u_center)+2]
    valid_depths = z_roi[(z_roi > 0) & (z_roi <= 80)]
    if len(valid_depths) == 0:
        raise ValueError("No valid depth values")
    # z = np.median(valid_depths)
    z = 1
    
    x_cam = (u_center - cx) * z / fx
    y_cam = (v_center - cy) * z / fy
    point_cam = np.array([x_cam, y_cam, z])

    # Convert to global coordinates
    point_world = cam_rot @ point_cam + cam_pos
    return point_world


def detect_objects(image):
    results = model(image)
    detections = []
    for box in results[0].boxes:
        cls_id = int(box.cls)
        if model.names[cls_id] in ['motorcycle', 'bicycle'] and box.conf > .2: 
            detections.append({
                'bbox': box.xyxy[0].tolist(),
                'class': model.names[cls_id]
            })
    return detections

def euclidean_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def  filter_detection(pos, cls, detections):
    new_pos = (pos[0], pos[1])
    results = []
    for det in detections:
        if det.get('class') == cls:
            print(det)
            print("-" *200)
            pos = det.get('position')
            distance = euclidean_distance(new_pos, (pos[0], pos[1]))
            results.append(distance)
    

    print(results,cls)
    if len(results) != 0:
        if (cls == 'motorcycle' and np.min(results) < 4) or (cls == 'bicycle' and np.min(results) < 4) :
            return True
    else:
        return False