import cv2
import mediapipe as mp
import numpy as np
import datetime
import time
from timeit import default_timer as timer
from CheatTrackers import CheatTracker,BlinkCheatTracker
from head_pose_estimation import headPose_solvePnP
from gaze_detection import gaze_detection
from helpers import fps_count
import config
import argparse


# MediaPipe face detection model
mp_face=mp.solutions.face_mesh
face_mesh=mp_face.FaceMesh(refine_landmarks=True)
drawing_spec=mp.solutions.drawing_utils.DrawingSpec(thickness=1,circle_radius=1)

# Coordinates for building a 3D face model
face_3d = np.array([
                      (0.0, 0.0, 0.0),       # Nose
                      (0.0, -330.0, -65.0),  # Chin
                      (-225.0, 170.0, -135.0),# Left eye corner
                      (225.0, 170.0, -135.0), # Right eye corner
                      (-150.0, -150.0, -125.0),# Left mouth corner
                      (150.0, -150.0, -125.0) # Right mouth corner
                     ])
 
# Indices of facial keypoints in MediaPipe
solvePnPLandmarks=[1,199,33,263,61,291]

# Eye and iris indices in MediaPipe
left_eye_points=[33,133,160,158,144]
left_iris_points=[468,469,470,471,472]
right_eye_points=[362,263,385,387,373]
right_iris_points=[473,474,475,476,477]


# Violation trackers; blink tracker works separately to avoid false positives during blinking
cheatTracker=CheatTracker()
blinkTracker=BlinkCheatTracker()

def parse_args():
    parser=argparse.ArgumentParser(description="Proctoring System")

    parser.add_argument("--video_source",type=str, help="Camera, remote camera URL, or video file")
    parser.add_argument("--output_file",type=str, help="Report file")
    parser.add_argument("--detection_window",type=int, help="Window for violation detection over N seconds")
    parser.add_argument("--detection_threshold",type=float, help="Analysis threshold")

    return parser.parse_args()

def main():

    args=parse_args()

    video_source=args.video_source if args.video_source is not None else config.VIDEO_SOURCE
    try:
        video_source=int(video_source)
    except ValueError:
        video_source=video_source

    output_file_path=args.output_file if args.output_file is not None else config.OUTPUT_FILE
    detection_window=args.detection_window if args.detection_window is not None else config.DETECTION_WINDOW
    detection_threshold=args.detection_threshold if args.detection_threshold is not None else config.DETECTION_THRESHOLD

    cap=cv2.VideoCapture(video_source) # If no webcam is available, a phone URL can be used
    
    # Read one frame to get camera parameters (height and width)
    ret,frame=cap.read()
    h,w,_=frame.shape

    # Focal length, usually equal to 1*w
    focal_length=1*w

    # Camera matrix, will be passed to solvePnP later
    cam_matrix=np.array([[focal_length,0,w/2],
                            [0,focal_length,h/2],
                            [0,0,1]])

    # Camera distortion parameters, default is 0
    dist_matrix=np.zeros((4,1),dtype=np.float64)
    
    # Start the stream
    while True:
        
        ret,frame=cap.read()

        # Record frame start time (useful for FPS calculation)
        start=time.time()

        # In case the camera is not found
        if not ret:
            print("Camera hasn`t been found")
            break

        # Convert frame to MediaPipe format
        rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        rgb.flags.writeable=False

        # Process frame with the model
        results=face_mesh.process(rgb)

        # Convert image format back
        rgb.flags.writeable=True
        rgb=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
        
        # If multiple faces are detected
        if results.multi_face_landmarks:
            # Iterate through detected face landmarks
            for face_landmarks in results.multi_face_landmarks:
                
                lm=face_landmarks.landmark

                # Get violation status
                text_2,y=headPose_solvePnP(lm=lm,solvePnPLandmarks=solvePnPLandmarks,
                                        face_3d=face_3d,cam_matrix=cam_matrix,dist_matrix=dist_matrix,
                                        frame=frame,w=w,h=h)           
                text_1=gaze_detection(lm=lm,y=y,left_eye_points=left_eye_points,left_iris_points=left_iris_points,
                                    right_eye_points=right_eye_points,right_iris_points=right_iris_points)

                # Display violations on frame
                cv2.putText(frame, text_1,(20,25),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,255),2)
                cv2.putText(frame,text_2,(20,50),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)
                
                # Run violation analysis
                cheatTracker.update(detection_window,detection_threshold,output_file_path,text_1,text_2)
                blinkTracker.update(detection_window,detection_threshold,output_file_path,text_1,text_2)

                # Calculate FPS
                fps_count(start=start,frame=frame)

        # If no faces are detected
        else:
            cv2.putText(
                frame,
                "No face!",
                (30,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0,0,255),
                2
            )

        # Show processed frame
        cv2.imshow("Proctoring",frame)

        # Press Esc to exit
        if cv2.waitKey(1)==27:
            break

    # Release camera and close window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
