import numpy as np

# Функция оценки положения зрачка
def gaze_detection(lm,y,left_eye_points,left_iris_points,right_eye_points,right_iris_points):

    # находим центр левого глаза и его зрачка
    left_eye_center=np.mean([[lm[idx].x,lm[idx].y] for idx in left_eye_points],axis=0)
    left_iris_center=np.mean([[lm[idx].x,lm[idx].y] for idx in left_iris_points],axis=0)

    # находим центр правого глаза и его зрачка    
    right_eye_center=np.mean([[lm[idx].x,lm[idx].y] for idx in right_eye_points],axis=0)
    right_iris_center=np.mean([[lm[idx].x,lm[idx].y] for idx in right_iris_points],axis=0)

    # находим высоту и ширину глаз, они нужны чтобы независимо от расстояния до камеры, отношения отклонений расстояний зрачка до центра оставались одинаковыми
    left_eye_top=np.mean([lm[159].y,lm[145].y])
    left_eye_bottom=np.mean([lm[33].y,lm[133].y])
    right_eye_top = np.mean([lm[386].y, lm[374].y])
    right_eye_bottom = np.mean([lm[263].y, lm[362].y])

    left_eye_middle=(left_eye_bottom+left_eye_top)/2
    right_eye_middle=(right_eye_bottom+right_eye_top)/2

    # усредняем высоту и ширину глаз
    eye_height=((left_eye_bottom-left_eye_top)+(right_eye_bottom-right_eye_top))/2
    eye_width=((lm[133].x-lm[33].x)+(lm[263].x-lm[362].x))/2
    
    # Так как веко перекрывает зрачок при взгляде вниз и определить положение зрачка трудно, было принято решение отслеживать взгляд вниз при помощи того, насколько закрыто веко
    dy_bottom=((left_iris_center[1]-left_eye_middle)+(right_iris_center[1]-right_eye_middle))/eye_height
    dy_bottom=np.clip(dy_bottom,0,1)

    dx=((left_eye_center[0]-left_iris_center[0])+(right_eye_center[0]-right_iris_center[0]))/(2*eye_width)
    dy_top=((left_eye_center[1]-left_iris_center[1])+(right_eye_center[1]-right_iris_center[1]))/(2*eye_width)

    # также готовим вывод признака
    text_2=""

    # отклонение взгляда по горизонтали, ранее переданный  угол y нужен чтобы учесть поворот самой головы 
    if dx>0.1 and y>-20:
        text_2+="Looking Right "
    elif dx<-0.1 and y<15:
        text_2+="Looking Left "
    else:
        text_2+=""

    # отклонение взгляда по вертикали
    if dy_top>0.04:
        text_2+="Looking Up "
    elif dy_bottom>0.15:
        text_2+="Looking Down "   
    else:
        text_2+=""

    # возвращаем текст
    return text_2