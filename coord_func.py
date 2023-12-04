import math


def get_coord(landmark, w, h):
    return (int(landmark.x*w), int(landmark.y*h))


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


