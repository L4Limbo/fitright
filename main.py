import mediapipe as mp
import cv2
import time
import math

from coord_func import *
from draw_image import draw_skeleton
from data_struct import create_struct


if __name__ == "__main__":
    mp_holistic = mp.solutions.holistic

    cap = cv2.VideoCapture(0)

    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        
        while cap.isOpened():

            ret, frame = cap.read()
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = image.shape[:2]
            results = holistic.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            """
            ist = get_angle(results, 12, 14, 16)
            leci = is_right(results, 12, 14, 16)

            if leci:
                clr = (255,255,0)
            else:
                clr = (255,0,255)
            
            cv2.putText(image, str(leci), (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, clr,  4, cv2.LINE_AA)
            """

            poi = create_struct(results)

            if results.pose_landmarks:
                draw_skeleton(image, results, w, h)

            cv2.imshow('Camera Feed', image)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


