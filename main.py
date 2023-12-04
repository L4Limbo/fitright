import mediapipe as mp
import cv2
import time
import math


def get_coord(landmark):
    return (int(landmark.x*w), int(landmark.y*h))


def line_betw(image, results, n1, n2):
    cv2.line(image, get_coord(results.pose_landmarks.landmark[n1]), get_coord(results.pose_landmarks.landmark[n2]), (0,0,255), 2)
    return None


def draw_skeleton(image, results):
    feat_list = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
    for i in feat_list:
        cv2.circle(image, get_coord(results.pose_landmarks.landmark[i]), 5, (0,255,0), 2)
    lines = ((11,12), (12,14), (14,16), (11,13), (13,15), (11,23), (24,12), (23,24), (25,23), (25,27), (24,26), (26,28))
    for points in lines:
        line_betw(image, results, points[0], points[1])                
    return None


def two_coord(results, n1, n2):
    x1 = results.pose_landmarks.landmark[n1].x
    x2 = results.pose_landmarks.landmark[n2].x
    y1 = results.pose_landmarks.landmark[n1].y
    y2 = results.pose_landmarks.landmark[n2].y

    return x1, y1, x2, y2


def three_coord(results, n1, n2, n3):
    x1 = results.pose_landmarks.landmark[n1].x
    x2 = results.pose_landmarks.landmark[n2].x
    x3 = results.pose_landmarks.landmark[n3].x

    y1 = results.pose_landmarks.landmark[n1].y
    y2 = results.pose_landmarks.landmark[n2].y
    y3 = results.pose_landmarks.landmark[n3].y

    return x1, y1, x2, y2, x3, y3


def get_dist(results, n1, n2):
    x1, y1, x2, y2 = two_coord(results, n1, n2)

    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5


def get_angle(results, n1, n2, n3):
    x1, y1, x2, y2, x3, y3 = three_coord(results, n1, n2, n3)
    v1 = (x1 - x2, y1 - y2)
    v2 = (x3 - x2, y3 - y2)
    dp = v1[0]*v2[0] + v1[1]*v2[1]
    mv1 = (v1[0]**2 + v1[1]**2)**0.5
    mv2 = (v2[0]**2 + v2[1]**2)**0.5
    angle = math.acos(dp/(mv1*mv2))

    return math.degrees(angle)


def is_straight(results, n1, n2, n3):
    if get_angle(results, n1, n2, n3)>160:
        return True
    return False


def is_right(results, n1, n2, n3):
    ang = get_angle(results, n1, n2, n3)
    if ang>80 and ang<100:
        return True
    return False


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

            
            ist = get_angle(results, 12, 14, 16)
            leci = is_right(results, 12, 14, 16)

            if leci:
                clr = (0,255,0)
            else:
                clr = (0,0,255)
            cv2.putText(image, str(leci), (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, clr,  4, cv2.LINE_AA)

            if results.pose_landmarks:
                draw_skeleton(image, results)

            cv2.imshow('Camera Feed', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break


    cap.release()
    cv2.destroyAllWindows()


