import cv2 as cv
import numpy as np
import mediapipe as mp
import math
import json
mp_face_mesh = mp.solutions.face_mesh

LEFT_EYE = [
362,
382,
381,
380,
374,
373,
390,
249,
263,
466,
388,
387,
386,
385,
384,
398,
]

#right eyes
RIGHT_EYE = [
33,
7,
163,
144,
145,
153,
154,
155,
133,
173,
157,
158,
159,
168,
161,
246,
]
#indices da iris
RIGHT_IRIS = [474, 475, 476, 477]
LEFT_IRIS = [469, 470, 471, 472]
L_H_LEFT = [33]     
L_H_RIGHT = [133]   
R_H_LEFT = [362]    
R_H_RIGHT = [263]

def euclidean_distance(point1, point2):
    x1, y1 =point1.ravel()
    x2, y2 =point2.ravel()
    distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    return distance
def iris_position(iris_center, right_point, left_point):
    center_to_right_dist = euclidean_distance(iris_center, right_point)
    total_distance = euclidean_distance(right_point, left_point)
    ratio = center_to_right_dist/total_distance
    iris_position =""
    # if ratio <= 0.42:
    #     iris_position="right"
    # elif ratio > 0.42 and ratio <= 0.57:
    #     iris_position="center"
    # else:
    #     iris_position = "left"
    if ratio <= 0.35:
        iris_position="right"
    elif ratio > 0.35 and ratio <= 0.60:
        iris_position="center"

    else:
        iris_position = "left"
    return iris_position, ratio
cap =cv.VideoCapture(0)
with mp_face_mesh.FaceMesh(
   max_num_faces=1,
   refine_landmarks=True,
   min_detection_confidence=0.5,
   min_tracking_confidence=0.5,
) as face_mesh:
    count1 =0
    count2 =0
    count3=0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv.flip (frame, 1)
        rgb_frame = cv.cvtColor (frame, cv.COLOR_BGR2RGB)
        img_h, img_w=frame.shape [:2]
        results = face_mesh.process (rgb_frame)
        if results.multi_face_landmarks:
        # print (results.multi_face_landmarks [0]. Landmark)
            mesh_points = np.array(
            [
                np.multiply([p.x, p.y], [img_w, img_h]).astype(int)
                for p in results.multi_face_landmarks[0].landmark
            ]
            )
            (l_cx, l_cy), l_radius = cv.minEnclosingCircle(mesh_points[LEFT_IRIS])
            (r_cx,r_cy), r_radius = cv.minEnclosingCircle(mesh_points[RIGHT_IRIS])
            center_left = np.array([l_cx, l_cy], dtype=np.int32)
            center_right = np.array([r_cx, r_cy], dtype=np.int32)
            cv.circle(frame, center_left, int(l_radius), (255, 0, 255), 1, cv.LINE_AA)
            cv.circle(frame, center_right, int(r_radius), (255, 0, 255), 1, cv.LINE_AA)
            cv.circle(frame, mesh_points[R_H_RIGHT][0], 3, (255, 255, 255), -1, cv.LINE_AA)
            cv.circle(frame, mesh_points[R_H_LEFT][0], 3, (0, 255, 255), -1, cv.LINE_AA)
            iris_pos, ratio = iris_position(center_right, mesh_points[R_H_RIGHT], mesh_points[R_H_LEFT][0])
            if(iris_pos=="right"):
                count1 += 1
            if count1 == 7:
                print("Action detected!-Right")
                action = {"action": "Movement"}
                with open(r"D:\Projects and codes\interview\resources\extinsion_interview\action.json", "w") as f:
                     json.dump(action, f)
                     f.close() 
                     count1 = 0
            if(iris_pos=="left"):
                count2 += 1
            if count2 == 7:
                print("Action detected!-Left")
                count2=0
                action = {"action": "Movement"}
                with open(r"D:\Projects and codes\interview\resources\extinsion_interview\action.json", "w") as f:
                     json.dump(action, f)
                     f.close() 
                     count1 = 0   
            if(iris_pos=="center"):
                # print("center")
                action = {"action": "Center"}
                with open(r"D:\Projects and codes\interview\resources\extinsion_interview\action.json", "w") as f:
                     json.dump(action, f)
                     f.close()
            import os
            if os.path.isfile('stop_recording'):
                print("inside it")
                os.remove('stop_recording')
                break      
        key = cv.waitKey(1)
        if key ==ord("q"):
            break
cap.release()
cv.destroyAllWindows()