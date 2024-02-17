import cv2
import mediapipe as mp
import numpy as np
import PoseDetector as pm
import time
import pygame
import threading


common = [0]
exit_event = threading.Event()
to_play = 0


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


def play_wav(file_path):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()


def play_sound():
    old_count = 0
    count_files={1:"one.wav", 2:"two.wav", 3:"three.wav", 4:"four.wav", 5:"five.wav", 6:"six.wav"}
    global to_play 
    while not exit_event.is_set():
        if old_count != common[0]:
            to_play = r'voice_comm\voice_comm\\' + str(count_files[common[0]])
            old_count = common[0]
        time.sleep(1)


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


def errorHandling(statelist):
    hip_timer = 0
    leg_timer = 0
    for state in statelist:
        if 'hip' in state[0] and state[1] > 0.15:
            hip_timer += state[1]
        if 'leg' in state[0] and state[1] > 0.15:
            leg_timer += state[1]
        if 'head' in state[0] and state[1] > 0.15:
            print('head wav')
            
    if hip_timer > 0 and hip_timer > leg_timer:
        print('hip wav')
        
    elif leg_timer > 0 and hip_timer < leg_timer:
        print('hip wav')
    
    

def main():
    global to_play
    pygame.init()
    pygame.mixer.init() 
    cap = cv2.VideoCapture('test.mp4')
    detector = pm.PoseDetector()
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
            head, shoulder, elbow, hip, leg, foot = get_pof(detector, img)

            # -------------------------------------------------------
            # state changes
            detected_current_state = currentState(head, shoulder, elbow, hip, leg, foot, detector.lmList, img)
            if (detected_current_state != 'pending'):
                if detected_current_state != current_state:
                    if((time.time() - start_time) >= 0.1):
                        current_state = detected_current_state
                        myLs = [current_state, time.time() - start_time]
                        stateTimeLs.append(myLs)
                        start_time = time.time()
                        print(stateTimeLs)
            # -------------------------------------------------------
            
            

            # -------------------------------------------------------
            # error handling
            errorHandling(stateTimeLs)
            # -------------------------------------------------------
            
            

            # ---------------------------------------------------------
            # count push up if 5 or more states availale
            # clean states starting from up (previous last state)
            if len(stateTimeLs) >= 5:                
                if count_pushups(stateTimeLs) > 0:
                    total_pushups += 1
                    common[0] = total_pushups
                    print(total_pushups)
                    stateTimeLs = [stateTimeLs[-1]]
            # ---------------------------------------------------------
            
            if to_play:
                print('==========================')
                play_wav(to_play)
                to_play = 0
                print('_+++=++++++++')
            # for debugging
            if (total_pushups == 5):
                print(stateTimeLs)
                # print(total_pushups)
                break
                        
        cv2.imshow('Pushup counter', img)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            exit_event.set()
            break
        
    cap.release()
    cv2.destroyAllWindows()
    print(total_pushups)
    
if __name__ == "__main__":
    thread = threading.Thread(target=play_sound)
    # Start threads
    thread.start()
    # Wait for threads to finish
    main()
    
    thread.join()
    
    

