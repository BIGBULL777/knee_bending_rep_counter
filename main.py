import cv2
import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose


mp_drawing = mp.solutions.drawing_utils

# Calculate angle
def calculate_angle(a, b, c):
    a = np.array(a) 
    b = np.array(b) 
    c = np.array(c) 
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360 - angle    
    return angle 


cap = cv2.VideoCapture('KneeBendVideo.mp4')

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
size = (width, height)
fps = int(cap.get(cv2.CAP_PROP_FPS))

relax_counter = 0 
bent_counter = 0
counter = 0
stage = None
feedback = None
images_array=[]


with mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence = 0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break


        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
      

        results = pose.process(image)
    
     
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        try:
            landmarks = results.pose_landmarks.landmark
            
   
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            

            angle = calculate_angle(hip, knee, ankle)


            a0 = int(ankle[0] * width)
            a1 = int(ankle[1] * height)

            k0 = int(knee[0] * width)
            k1 = int(knee[1] * height)

            h0 = int(hip[0] * width)
            h1 = int(hip[1] * height)

            cv2.line(image, (h0, h1), (k0, k1), (255, 255, 0), 2)
            cv2.line(image, (k0, k1), (a0, a1), (255, 255, 0), 2)
            cv2.circle(image, (h0, h1), 5, (0, 0, 0), cv2.FILLED)
            cv2.circle(image, (k0, k1), 5, (0, 0, 0), cv2.FILLED)
            cv2.circle(image, (a0, a1), 5, (0, 0, 0), cv2.FILLED)       
            
            
            cv2.putText(image, str(round(angle,4)), tuple(np.multiply(shoulder, [640, 480]).astype(int)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            
            relax_time = (1 / fps) * relax_counter
            bent_time = (1 / fps) * bent_counter

 
            if angle > 140:
                relax_counter += 1
                bent_counter = 0
                stage = "Relaxed"
                feedback = ""
            
            if angle < 140:
                relax_counter = 0
                bent_counter += 1
                stage = "Bent"
                feedback = ""
            

            if bent_time == 8:
                counter += 1
                feedback = 'Rep completed'
                
            elif bent_time < 8 and stage == 'Bent':
                feedback = 'Keep Your Knee Bent'
            
            else:
                feedback = ""
                
        except:
            pass
                

        cv2.rectangle(image, (0,0), (int(width), 60), (0,0,0), -1)
        

        cv2.putText(image, 'REPS', (10,15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        
        cv2.putText(image, str(counter), 
                    (10,50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        
        cv2.putText(image, 'FEEDBACK', (315,15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        
        cv2.putText(image, feedback, 
                    (315,50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        
        cv2.putText(image, str(round(bent_time,2)), 
                    (725,50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)  

        images_array.append(image) 
        
        cv2.imshow('Knee Bend Excercise', image)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


out = cv2.VideoWriter('Output.mp4', cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
for i in range(len(images_array)):
    out.write(images_array[i])
out.release()