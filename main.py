import cv2
import mediapipe as mp
import numpy as np
import PoseDetector as pm
import time
import pygame
import threading


pygame.init()
pygame.mixer.init()


def play_wav(file_path):
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        
def play_wav_not_busy(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
        
        
def get_pof(detector, img):
    return (
        detector.findAngle(img, 7, 11, 23),  # head
        detector.findAngle(img, 13, 11, 23), # shoulder
        detector.findAngle(img, 11, 13, 15), # elbow
        detector.findAngle(img, 11, 23,25),  # hip
        detector.findAngle(img, 23, 25, 27), # leg
        detector.findAngle(img, 25, 27, 31)  # foot
    )


def count_pushup(statelist):
    steps = ['up', 'transit', 'down', 'transit', 'up']
    pushups = 0
    i = 0
    next_step = steps[i]
    
    for step in statelist:
        if next_step in step[0]:
            i += 1
            if i == 5: return 1
            next_step = steps[i]
 
            
    return 0
    
    
def right_form(head, shoulder, elbow, hip, leg, foot, lmlist, img):
    return  (hip > 155 and leg > 150)


def standing(lmlist, img):
    return abs(lmlist[11][1] - lmlist[27][1]) < 0.3 * img.shape[1]


# STATES
def upState(shoulder, elbow):
    if (elbow > 160):
        return True
    return False


def downState(shoulder, elbow):
    if (elbow < 95):
        return True
    return False


def transitState(head, shoulder, elbow, hip, leg, foot):
    if (elbow < 160 and elbow > 95):
        return True
    return False


def wrongForm(head, shoulder, elbow, hip, leg, foot):
    if hip < 155:
        return '-hip'
    if leg < 150:
        return '-leg'        
    return ''
    

def currentState(head, shoulder, elbow, hip, leg, foot, lmlist, img):
    if standing(lmlist, img):
        return 'standing'
    elif upState(shoulder, elbow):
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
    
    
def errorHandling(statelist):
    if statelist[-1][0] == 'standing':
        return statelist
    
    hip_timer = 0
    leg_timer = 0
    
    for state in statelist:
        if 'hip' in state[0] and state[1] > 0.1:
            hip_timer += state[1]
        if 'leg' in state[0] and state[1] > 0.1:
            leg_timer += state[1]
            
    if hip_timer > 0.5:
        print('1: ',time.time())
        play_wav(r'voice_comm\\' + 'fix_back.wav')
        print('2: ', time.time())
        return [[entry[0].replace('-hip', '').replace('hip-', '').replace('hip', ''), entry[1]] for entry in statelist]
        
    elif leg_timer > 0.5 and hip_timer < leg_timer:
        print('1: ',time.time())
        play_wav(r'voice_comm\\' + 'fix_knees.wav')
        print('2: ', time.time())
        return  [[entry[0].replace('-leg', '').replace('leg-', '').replace('leg', ''), entry[1]] for entry in statelist]
    
    return statelist


def deadHandling(statelist):
    total_time = 0
    for state in statelist:
        if 'up' not in state[0] and 'standing' not in state[0]:
            total_time += state[1]
    if total_time > 4:
        return 'tired'
    return 0


def standingHandling(statelist, totalPushups):
    for state in statelist:
        if state[0] == 'standing' and state[1] > 0.5:
            print("Reset Pushups")
            return 0
    else:
        return totalPushups


def main():
    # cap = cv2.VideoCapture('test_2.mp4')
    cap = cv2.VideoCapture('slow_video.mp4')
    detector = pm.PoseDetector()
    total_pushups = 0
    goal_pushups = 5
    stateTimeLs = [['pending', 0]]
    current_state = 'pending'
    start_time = time.time()
    session_time = time.time()
    last_error_handling_time = time.time()
    im_tired = False
    count_files={1:"one.wav", 2:"two.wav", 3:"three.wav", 4:"four.wav", 5:"five.wav", 6:"six.wav"}

    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    while cap.isOpened():
        ret, img = cap.read() #1280 x 720
        
        if not ret: 
            break
        
        img = detector.findPose(img, False)
        lmList = detector.findPosition(img, False)
        
        
        if len(lmList) != 0:
            head, shoulder, elbow, hip, leg, foot = get_pof(detector, img)           
            
            detected_current_state = currentState(head, shoulder, elbow, hip, leg, foot, detector.lmList, img)
            if detected_current_state != current_state:
                if ((time.time() - start_time) >= 0.1):
                    current_state = detected_current_state
                    stateTimeLs.append([current_state, time.time() - start_time])
                    start_time = time.time()
                print(stateTimeLs)
            
            
            if count_pushup(stateTimeLs) == 1:
                total_pushups += 1
                stateTimeLs = [stateTimeLs[-1]]
                print("Pushups: ", total_pushups)
                play_wav(r'voice_comm\\' + count_files[total_pushups])
         
        
            if time.time() - last_error_handling_time >= 2:
                stateTimeLs = errorHandling(stateTimeLs)
                last_error_handling_time = time.time()
            
            if im_tired != True:
                tired = deadHandling(stateTimeLs)
                if tired:
                    play_wav_not_busy(r'voice_comm\\' + 'tired.wav')
                    goal_pushups -= 2
                    im_tired = True
            
            total_pushups = standingHandling(stateTimeLs, total_pushups)
            

            if total_pushups >= goal_pushups:
                print("Congrats: " + str(total_pushups))
                play_wav_not_busy(r'voice_comm\\' + count_files[total_pushups])
                time.sleep(1)
                play_wav_not_busy(r'voice_comm\\' + 'congrats.wav')
                while pygame.mixer.music.get_busy():  # Wait for the audio to finish
                    time.sleep(0.1)  # Check every 0.1 seconds
                break
        
        
        cv2.imshow('Pushup counter', img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            print(total_pushups)
            break
        
        
    cap.release()
    cv2.destroyAllWindows()



if __name__ == "__main__":
    main()
