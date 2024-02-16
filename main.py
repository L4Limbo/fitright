import cv2
import mediapipe as mp
import numpy as np
import PoseDetector as pm
import time



def get_pof(detector, img):
    return (
        detector.findAngle(img, 7, 11, 23),  # head
        detector.findAngle(img, 13, 11, 23), # shoulder
        detector.findAngle(img, 11, 13, 15), # elbow
        detector.findAngle(img, 11, 23,25),  # hip
        detector.findAngle(img, 23, 25, 27), # leg
        detector.findAngle(img, 25, 27, 31)  # foot
    )


def get_pushup_percentages(elbow, shoulder):
    return (
        np.interp(elbow, (90, 160), (0, 100)),
        np.interp(shoulder, (0, 60), (0, 100))
    )
    
    
def right_form(head, shoulder, elbow, hip, leg, foot, lmlist, img):
    return  (hip > 155 and leg > 150) and abs(lmlist[11][1] - lmlist[27][1]) > 0.1 * img.shape[1]


# STATES
def upState(shoulder, elbow):
    if (elbow > 160 and shoulder > 40):
        return True
    return False


def downState(shoulder, elbow):
    if (elbow < 95 and shoulder < 20):
        return True
    return False


def transitState(head, shoulder, elbow, hip, leg, foot):
    if (elbow < 155 and elbow > 95):
        return True
    return False



def wrongForm(head, shoulder, elbow, hip, leg, foot):
    if hip < 150:
        return '-hip'
    if leg < 145:
        return '-leg'
    if head < 152:
        return '-head'        
    return ''


def currentState(head, shoulder, elbow, hip, leg, foot, lmlist, img):
    if upState(shoulder, elbow):
        if right_form(head, shoulder, elbow, hip, leg, foot, lmlist, img):
            return 'up'
        return 'up'  + wrongForm(head, shoulder, elbow, hip, leg, foot)
    
    elif downState(shoulder, elbow):
        if right_form(head, shoulder, elbow, hip, leg, foot, lmlist, img):
            return 'down'
        return 'down' + wrongForm(head, shoulder, elbow, hip, leg, foot)
    
    elif transitState(head, shoulder, elbow, hip, leg, foot):
        if right_form(head, shoulder, elbow, hip, leg, foot, lmlist, img):
            return 'transit'
        return 'transit' + wrongForm(head, shoulder, elbow, hip, leg, foot)   
    else:
        return 'pending'
    
    
def count_pushups(statelist):
    steps = ['up', 'transit', 'down', 'transit', 'up']
    pushups = 0
    i = 0
    next_step = steps[i]
    
    for step in statelist:
        if next_step in step[0]:
            i += 1
            next_step = steps[i]
            
        if i == 4:
            pushups +=1 
            i = 1
            next_step = steps[i]
            
    return pushups
    
    
def main():
    cap = cv2.VideoCapture(0)
    detector = pm.PoseDetector()
    count = 0
    direction = 0
    form = 0
    feedback = "Fix Form"
    stateTimeLs = []
    current_state = 'pending'
    start_time = time.time()
    session_time = time.time()
    total_pushups = 0

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
    while cap.isOpened():
        _, img = cap.read() #1280 x 720
        
        img = detector.findPose(img, False)
        lmList = detector.findPosition(img, False)

        if len(lmList) != 0:
            # points of interest
            head, shoulder, elbow, hip, leg, foot = get_pof(detector, img)
            
            # pushup percentages
            elbow_per, shoulder_per = get_pushup_percentages(elbow, shoulder)
            
            #Check to ensure right form before starting the program
            if right_form(head, shoulder, elbow, hip, leg, foot, detector.lmList, img):
                form = 1

        
            detected_current_state = currentState(head, shoulder, elbow, hip, leg, foot, detector.lmList, img)
            
            if (detected_current_state != 'pending'):
                if detected_current_state != current_state:
                    if((time.time() - start_time) >= 0.2):
                        myLs = [current_state,time.time() - start_time]
                        stateTimeLs.append(myLs)
                        
                        current_state = detected_current_state
                        start_time = time.time()
                        print(stateTimeLs)
                        print('--------------------------' + str(total_pushups))                
            
            if len(stateTimeLs) >= 5:    
                total_pushups = count_pushups(stateTimeLs)
            #Check for full range of motion for the pushup
            if form == 1: # up 
                if elbow_per == 0:
                    if elbow <= 90 and hip > 160:
                        feedback = "Up"
                        if direction == 0:
                            count += 0.5
                            direction = 1
                    else:
                        # conditions for each error
                        feedback = "Fix Form"
                        
                if elbow_per == 100:
                    if elbow > 160 and shoulder > 40 and hip > 160:
                        feedback = "Down"
                        if direction == 1:
                            count += 0.5
                            direction = 0
                    else:
                        # conditions for each error
                        feedback = "Fix Form"
            
            if (total_pushups == 5):
                print(stateTimeLs)
                print(total_pushups)
                break
                        
        cv2.imshow('Pushup counter', img)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()
    
    
if __name__ == "__main__":
    main()
    
    
    

