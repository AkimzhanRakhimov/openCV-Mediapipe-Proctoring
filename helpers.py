import cv2
import time
import os
import json

# Calculate FPS
def fps_count(start,frame):
    end=time.time()
    totalTime=end-start
    fps=1/totalTime

    cv2.putText(frame, f'FPS: {int(fps)}',(20,450),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)

def save_report(output_file_path,data):
    # If the report exists, append a new violation to it
    if os.path.exists(output_file_path):
        with open(output_file_path,"r+") as f:
            try:
                # Load the existing list of violations
                old_data=json.load(f)
            except json.JSONDecodeError:
                # If an error occurs, create a new empty list of violations
                old_data=[]
            # Add new violation to the list
            old_data.append(data)
            # Clear old data and write updated list
            f.seek(0)
            # Finish writing JSON
            json.dump(old_data,f,indent=2)
    else:
        # If file does not exist, create a new one
        with open(output_file_path,"w") as f:
            # Finish writing JSON
            json.dump([data],f)
