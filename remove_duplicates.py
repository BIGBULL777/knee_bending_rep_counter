import cv2
import hashlib


cap = cv2.VideoCapture('KneeBendVideo.mp4')

frames = []


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    

    hash_value = hashlib.sha256(frame).hexdigest()
    

    frames.append((frame, hash_value))
    print(hash_value)


for i in range(len(frames)):
    for j in range(i+1, len(frames)):
        if frames[i][1] == frames[j][1]:
            print("Found duplicate frames at index {} and {}".format(i, j))