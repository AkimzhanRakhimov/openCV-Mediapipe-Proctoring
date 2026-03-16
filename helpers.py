import cv2
import time
import os
import json
# считаем фпс
def fps_count(start,frame):
    end=time.time()
    totalTime=end-start
    fps=1/totalTime

    cv2.putText(frame, f'FPS: {int(fps)}',(20,450),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)

def save_report(output_file_path,data):
    # Если отчет существует, то дописываем новое нарушение в него
    if os.path.exists(output_file_path):
        with open(output_file_path,"r+") as f:
            try:
                # Загружаем старый список нарушений
                old_data=json.load(f)
            except json.JSONDecodeError:
                # В случае ошибки создаем новый пустой список нарушений
                old_data=[]
            # Добавляем новое нарушение в список
            old_data.append(data)
            # Стираем старый список и записываем обновленный
            f.seek(0)
            # Завершаем дамп
            json.dump(old_data,f,indent=2)
    else:
        # Если файла нет, то создаем новый
        with open(output_file_path,"w") as f:
            # Завершаем дамп
            json.dump([data],f)