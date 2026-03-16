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


# Модель mediapipe для обнаружения лица
mp_face=mp.solutions.face_mesh
face_mesh=mp_face.FaceMesh(refine_landmarks=True)
drawing_spec=mp.solutions.drawing_utils.DrawingSpec(thickness=1,circle_radius=1)

# Координаты для построения 3д модели лица
face_3d = np.array([
                      (0.0, 0.0, 0.0),       #Нос
                      (0.0, -330.0, -65.0),  #Челюсть
                      (-225.0, 170.0, -135.0),#Угол левого глаза
                      (225.0, 170.0, -135.0), #Угол правого глаза
                      (-150.0, -150.0, -125.0),#Левый край рта
                      (150.0, -150.0, -125.0) #Правый край рта
                     ])
 
# Индексы ключевых точек лица в mediapipe
solvePnPLandmarks=[1,199,33,263,61,291]

# Индексы глаз и зрачков в mediapipe
left_eye_points=[33,133,160,158,144]
left_iris_points=[468,469,470,471,472]
right_eye_points=[362,263,385,387,373]
right_iris_points=[473,474,475,476,477]


# Объекты трекеров нарушений, трекер зрачка по направлению вниз работает отдельно чтобы избежать ложного срабатывания при моргании
cheatTracker=CheatTracker()
blinkTracker=BlinkCheatTracker()

def parse_args():
    parser=argparse.ArgumentParser(description="Proctoring System")

    parser.add_argument("--video_source",type=str, help="Камера, ссылка на удаленную камеру, видео файл")
    parser.add_argument("--output_file",type=str, help="Файл репорта")
    parser.add_argument("--detection_window",type=int, help="Окно для проверки нарушений за N секунд")
    parser.add_argument("--detection_threshold",type=float, help="Порог для анализа")

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

    cap=cv2.VideoCapture(video_source) # Если нет веб камеры, можно использовать url телефона
    
    # Читаем камеру единожды чтобы достать ее параметры (высоты и ширины)
    ret,frame=cap.read()
    h,w,_=frame.shape

    # Фокусное расстояние, обычно равно 1*w
    focal_length=1*w

    # Матрица камеры, позже ее нужно передать в алгоритм solvePnP 
    cam_matrix=np.array([[focal_length,0,w/2],
                            [0,focal_length,h/2],
                            [0,0,1]])

    # Параметры искажения камеры, по умолчанию равно 0
    dist_matrix=np.zeros((4,1),dtype=np.float64)
    
    # Запускаем поток
    while True:
        
        ret,frame=cap.read()

        # Отсчитваем время записи фрейма, пригодиться для подсчета фпс
        start=time.time()

        # На случай если камера не была найдена
        if not ret:
            print("Camera hasn`t been found")
            break

        # Переводим изображений с потока в формат работы MediaPipe
        rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        rgb.flags.writeable=False
        # Обрабатываем результат со помощью модели

        results=face_mesh.process(rgb)

        # Переводим формат изображения обратно
        rgb.flags.writeable=True
        rgb=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
        
        # На случай если обнаружено несколько лиц
        if results.multi_face_landmarks:
            # Берем найденные моделью точки на лицах 
            for face_landmarks in results.multi_face_landmarks:
                
                lm=face_landmarks.landmark

                # Возвращаем ответ о том, было ли нарушение
                text_2,y=headPose_solvePnP(lm=lm,solvePnPLandmarks=solvePnPLandmarks,
                                        face_3d=face_3d,cam_matrix=cam_matrix,dist_matrix=dist_matrix,
                                        frame=frame,w=w,h=h)           
                text_1=gaze_detection(lm=lm,y=y,left_eye_points=left_eye_points,left_iris_points=left_iris_points,
                                    right_eye_points=right_eye_points,right_iris_points=right_iris_points)

                # Выводим нарушение на фрейм
                cv2.putText(frame, text_1,(20,25),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,255),2)

                cv2.putText(frame,text_2,(20,50),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)
                
                # Запускаем анализ нарушений
                cheatTracker.update(detection_window,detection_threshold,output_file_path,text_1,text_2)
                blinkTracker.update(detection_window,detection_threshold,output_file_path,text_1,text_2)

                # Считаем фпс
                fps_count(start=start,frame=frame)

        # Если не было обнаружено ни одного лица
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


        # Выводим обработанное изображение
        cv2.imshow("Proctoring",frame)

        # Чтобы выйти необходимо нажать Esc
        if cv2.waitKey(1)==27:
            break

    # Закрываем камеру и окно
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()