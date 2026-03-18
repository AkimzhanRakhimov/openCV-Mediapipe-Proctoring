import numpy as np
import cv2

# Head pose estimation function
def headPose_solvePnP(lm,solvePnPLandmarks,face_3d,cam_matrix,dist_matrix,frame,w,h):
    face_2d=np.array([[int(lm[id].x*w),int(lm[id].y*h)] for id in solvePnPLandmarks],dtype=np.float64)
            
    # Main algorithm that returns rotation and translation vectors of the face
    success, rotation_vector, translation_vector = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix, flags=cv2.SOLVEPNP_ITERATIVE)

    # Convert rotation vector to rotation matrix
    rmat,jac=cv2.Rodrigues(rotation_vector)

    # Extract angles
    angles,mtxR,mtxQ,Qx,Qy,Qz=cv2.RQDecomp3x3(rmat)

    # X angle can be in range ±180, normalize it
    x=angles[0]
    if x > 90:
        x -= 180
    elif x < -90:
        x+=180
    else:
        x=x
    y=angles[1]
    z=angles[2]

    # Prepare violation text
    text=""

    # Horizontal rotation
    if y<-35:
        text+="Turned head Left "
    elif y>35:
        text+="Turned head Right "
    else:
        text=""
    # Vertical rotation
    if x<-20:
        text+="Turned head Up "
    elif x>15:
        text+="Turned head Down "
    else:
        text+=""
    
    # Draw facial keypoints
    for p in face_2d:
        cv2.circle(frame, (int(p[0]), int(p[1])), 3, (0,0,255), -1)

    # Draw head pose direction using the nose
    nose_end_point2D, jacobian = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector, translation_vector, cam_matrix, dist_matrix)

    point1 = ( int(face_2d[0][0]), int(face_2d[0][1]))
    
    point2 = ( int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
    
    cv2.line(frame, point1, point2, (255,255,255), 2)

    # Display angles
    cv2.putText(frame,"x: "+str(np.round(x,2)),(500,50),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
    cv2.putText(frame,"y: "+str(np.round(y,2)),(500,100),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
    cv2.putText(frame,"z: "+str(np.round(z,2)),(500,150),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)

    # Return text and horizontal head rotation angle (used later)
    return text,y
