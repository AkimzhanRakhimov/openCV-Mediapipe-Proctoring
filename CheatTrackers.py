import time
from datetime import datetime
import json
import os
from helpers import save_report


# Класс, который анализирует нарушения
class CheatTracker:

    # Начальные параметры трекера
    def __init__(self):
        # Трекер будет считать процент нарушений за количество времени n
        self.duration=0
        self.native_frames_count=0
        self.banned_frames_count=0
        self.last_relation=0
        self.reported=False
        self.reason=""
        self.last_time=time.time()

    # Отслеживание нарушений во времени
    def update(self,n,threshold,output_file_path,text_1,text_2):
        # Берем нынешнее время
        now=time.time()
        # Duration накапливает отрезки времени между нынешним и последним фреймом
        self.duration+=now-self.last_time
        # Устанавливаем последнее время фрейма
        self.last_time=now
        # Считаем общее число фреймов
        self.native_frames_count+=1
        # Считаем отношение фреймов с нарушениями к общему числу фреймов 
        relative_frames_count=self.banned_frames_count/self.native_frames_count
        # Проверяем содержимое text 1 и text 2, в случае если text 1 ложно срабатывает из за моргания, то идет обработка через отдельный подкласс
        self.analyse_frame(text_1=text_1,text_2=text_2)
        # Выводим длительность окна, отношение фреймов и пиковое значение отношения фреймов
        print(f"Duration: {self.duration},RFC: {relative_frames_count}, Last RFC: {self.last_relation}")
        # Если длительность окна равна n секунд, начинаем проверку
        if self.duration>n:
            # Если в промежутке временного окна число нарушений превысило порог, то наказываем
            if relative_frames_count>threshold:
                # Если нынешнее отношение фреймов выше предыдущего, то увеличиваем его
                if relative_frames_count>self.last_relation:
                    self.last_relation=relative_frames_count
            # Если же нарушений не было, то сбрасываем трекер
            else:
                self.reset()
            
            # Здесь мы считаем разницу между последним пиковым отношением фреймов и нынешним, если оно больше 0.05, вероятно, человек перестал читерить, значит можно фиксировать нарушение 
            if self.last_relation-relative_frames_count>=0.05 and not self.reported:
                # Выводим сообщение о нарушении
                print(f"Relation of banned frames: {relative_frames_count}, Period: {int(self.duration)} seconds, Reason: {self.reason}")
                # Извлекаем нынешнюю дату и время
                dt=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Подготавливаем сообщение в формат JSON
                data={"Relation of banned frames":relative_frames_count, "Period":int(self.duration), "Reason":self.reason, "Date":dt}
                # Сохраняем репорт
                save_report(output_file_path,data)
                # Ставим флажок о том что репорт совершен
                self.reported=True
                # Сбрасываем трекер
                self.reset()
                    
        else:
            # Флажок репорта по умолчанию
            self.reported=False
    
    # Этот метод нужен чтобы ограничить трекер от ложного срабатывания при моргании, а также для записи признака нарушения    
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
        
            
    # Метод для сброса переменных трекера
    def reset(self):
        self.duration=0
        self.last_relation=0
        self.native_frames_count=0
        self.banned_frames_count=0
        self.reason=""
        self.last_time=time.time()

# Отдельный подкласс, который обрабатывает взгляд вниз и защищает от ложного срабатывания при моргании
class BlinkCheatTracker(CheatTracker):
    def __init__(self):
        super().__init__()

    def analyse_frame(self, text_1,text_2=None):
        if text_1=="Looking Down ":
            self.banned_frames_count+=1
            if self.banned_frames_count/self.native_frames_count>0.2:
                self.reason=text_1
        