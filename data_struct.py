
def create_struct(results):

    points_of_interest = {}
    
    if not results.pose_landmarks:
        return 0
    
    for i in range(11,33):
        point = results.pose_landmarks.landmark[i]
        points_of_interest[i] = (point.x, point.y)

    return points_of_interest


