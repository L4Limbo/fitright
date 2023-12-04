import cv2

#funcs painting over video
def get_coord(landmark, w, h):
    return (int(landmark.x*w), int(landmark.y*h))


def line_betw(image, results, n1, n2, w, h):
    cv2.line(image, get_coord(results.pose_landmarks.landmark[n1], w, h), get_coord(results.pose_landmarks.landmark[n2], w, h), (0,0,255), 2)
    return None


def draw_skeleton(image, results, w, h):
    feat_list = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
    for i in feat_list:
        cv2.circle(image, get_coord(results.pose_landmarks.landmark[i], w, h), 5, (0,255,0), 2)
    lines = ((11,12), (12,14), (14,16), (11,13), (13,15), (11,23), (24,12), (23,24), (25,23), (25,27), (24,26), (26,28))
    for points in lines:
        line_betw(image, results, points[0], points[1], w, h)                
    return None


