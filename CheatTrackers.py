import time
from datetime import datetime
import json
import os
from helpers import save_report


# Class that analyzes violations
class CheatTracker:

    # Initial tracker parameters
    def __init__(self):
        # Tracker calculates the percentage of violations over a time window n
        self.duration=0
        self.native_frames_count=0
        self.banned_frames_count=0
        self.last_relation=0
        self.reported=False
        self.reason=""
        self.last_time=time.time()

    # Track violations over time
    def update(self,n,threshold,output_file_path,text_1,text_2):
        # Get current time
        now=time.time()
        # Duration accumulates time between current and previous frame
        self.duration+=now-self.last_time
        # Update last frame time
        self.last_time=now
        # Count total frames
        self.native_frames_count+=1
        # Calculate ratio of violating frames to total frames
        relative_frames_count=self.banned_frames_count/self.native_frames_count
        # Analyze frame content; text_1 false positives (blinks) are handled in subclass
        self.analyse_frame(text_1=text_1,text_2=text_2)
        # Print window duration, frame ratio, and peak ratio
        print(f"Duration: {self.duration},RFC: {relative_frames_count}, Last RFC: {self.last_relation}")
        
        # If time window reached n seconds, start evaluation
        if self.duration>n:
            # If violation ratio exceeds threshold, apply penalty logic
            if relative_frames_count>threshold:
                # Update peak ratio if current is higher
                if relative_frames_count>self.last_relation:
                    self.last_relation=relative_frames_count
            # If no significant violations, reset tracker
            else:
                self.reset()
            
            # If drop from peak ratio is significant, assume cheating stopped → log violation
            if self.last_relation-relative_frames_count>=0.05 and not self.reported:
                # Print violation message
                print(f"Relation of banned frames: {relative_frames_count}, Period: {int(self.duration)} seconds, Reason: {self.reason}")
                # Get current date and time
                dt=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Prepare JSON report
                data={"Relation of banned frames":relative_frames_count, "Period":int(self.duration), "Reason":self.reason, "Date":dt}
                # Save report
                save_report(output_file_path,data)
                # Mark as reported
                self.reported=True
                # Reset tracker
                self.reset()
                    
        else:
            # Reset reported flag by default
            self.reported=False
    
    # This method prevents false positives (e.g., blinking) and records violation reason    
    def analyse_frame(self,text_1,text_2):
        if text_1 or text_2:
            self.reason=""
            if text_1 and text_2:
                self.banned_frames_count+=1
                if text_1!="Looking Down ":
                    self.reason+=text_1
                self.reason+=text_2
            elif text_1:
                if text_1!="Looking Down ":
                    self.reason+=text_1
                    self.banned_frames_count+=1 
            elif text_2:
                self.reason+=text_2
                self.banned_frames_count+=1
        else:
            self.reason=self.reason
        
            
    # Reset tracker variables
    def reset(self):
        self.duration=0
        self.last_relation=0
        self.native_frames_count=0
        self.banned_frames_count=0
        self.reason=""
        self.last_time=time.time()


# Separate subclass to handle downward gaze and avoid false positives from blinking
class BlinkCheatTracker(CheatTracker):
    def __init__(self):
        super().__init__()

    def analyse_frame(self, text_1,text_2=None):
        if text_1=="Looking Down ":
            self.banned_frames_count+=1
            if self.banned_frames_count/self.native_frames_count>0.2:
                self.reason=text_1
