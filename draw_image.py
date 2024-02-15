import cv2


#funcs painting over video
def get_coord(landmark, w, h):
    return (int(landmark.x*w), int(landmark.y*h))


def line_betw(image, results, n1, n2, w, h):
    cv2.line(image, get_coord(results.pose_landmarks.landmark[n1], w, h), get_coord(results.pose_landmarks.landmark[n2], w, h), (0,0,255), 2)
    return None


def center_of_line(image, results, n1, n2, w, h):
    le_x, le_y = get_coord(results.pose_landmarks.landmark[n1],w, h)
    re_x, re_y = get_coord(results.pose_landmarks.landmark[n2],w, h)
    
    return (le_x+re_x)//2, (le_y +re_y)//2
 

def draw_skeleton(image, results, w, h):
    feat_list = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 23, 24, 25, 26, 27, 28,]
    mhx, mhy = center_of_line(image, results, 7, 8, w, h)
    msx, msy = center_of_line(image, results, 11, 12, w, h)

    cv2.circle(image, (mhx, mhy), 5, (0,255,0), 2)
    cv2.circle(image, (msx, msy), 5, (0,255,0), 2)
    
    cv2.line(image, (mhx,mhy), (msx, msy), (0,0,255), 2)

    for i in feat_list:
        cv2.circle(image, get_coord(results.pose_landmarks.landmark[i], w, h), 5, (0,255,0), 2)
        cv2.putText(image, str(i), get_coord(results.pose_landmarks.landmark[i], w, h), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    lines = ((11,12), (12,14), (14,16), (11,13), (13,15), (11,23), (24,12), (23,24), (25,23), (25,27), (24,26), (26,28), (20,18), (18,16), (16,20), (15,19), (19,17), (15,17))
    for points in lines:
        line_betw(image, results, points[0], points[1], w, h)                
    return None


