from tkinter import *
from math import sqrt
from threading import Thread, Event
from tkinter import ttk
from PIL import ImageTk, Image
import os
import ctypes
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def work_font(event, N):
    label = event.widget
    size = int((label.cget("font").split())[1])
    if size < (event.height / N):
        label.configure(font=("", size + 1))
    else:
        if size > 0:
            label.configure(font=("", size - 1))


def update_Q(x):
    global Qm, QIN, rotametr, VENT_LABEL, VENT1, VENT2, number_rotametr_photo, rotametr_label, truba_label

    # Проверяем, инициализированы ли все необходимые компоненты
    if 'rotametr_label' not in globals() or 'rotametr_photo_list' not in globals():
        return

    if x == '-':
        if Qm != 0:
            Qm -= 2.5
            number_rotametr_photo -= 1
            if Qm == 0:
                QIN = 0
                number_rotametr_photo = 0
                VENT_LABEL.configure(image=VENT1)
                truba_label.configure(image=truba_image)
            else:
                QIN = round(0.0028 * (Qm / 100), 6)
    elif x == '+':
        VENT_LABEL.configure(image=VENT2)
        truba_label.configure(image=truba_image2)
        if Qm < 100:
            Qm += 2.5
            QIN = round(0.0028 * (Qm / 100), 6)
            number_rotametr_photo += 1

    # Ограничиваем номер фото в допустимых пределах
    number_rotametr_photo = max(0, min(number_rotametr_photo, len(rotametr_photo_list) - 1))

    rotametr_label.configure(image=rotametr_photo_list[number_rotametr_photo])
    Q.config(text=f"{Qm}%")
    rotametr.config(text=f'Показания\nротаметра\n{round(QIN * 1000 * 3600, 0)} л/ч')
    RWIL.configure(image=rotametr_water_img)
    RWIL.image = rotametr_water_img


class Bak():
    def __init__(self, place, number):
        self.m = 0.0
        self.S = 1
        self.h = 40
        self.H = 0
        self.Q_in = 0
        self.Q_out = 0
        self.number = number
        self.W_can = 607
        self.H_can = 490

        self.pil_water = Image.open(resource_path("photo/water.png"))
        self.pil_image = self.pil_water.resize((600, 1))
        self.water_image = ImageTk.PhotoImage(self.pil_image)

        self.BAK = Label(can, image=photo_bak, borderwidth=0)
        self.BAK.place(relx=0.361 + (number * 0.31), rely=0.027 + (number * 0.487), relwidth=0.1479, relheight=0.4665)

        self.water = Label(can, image=self.water_image, borderwidth=0, background="#C3C3C3", anchor=S)
        self.water.place(relx=0.374 + (number * 0.31), rely=0.06 + (number * 0.491), relwidth=0.122, relheight=0.355)

        self.V = Label(can, image=VENT1, borderwidth=0)
        self.V.place(relx=0.51 + (number * 0.31), rely=0.4279 + (number * 0.486), relwidth=0.178, relheight=0.0855)

        self.name = Label(can, text=f'Уровень {number + 1}', width=10, background=can["background"], font=("", 7))
        self.name.place(relx=0.52 + (number * 0.31), rely=0.18 + (number * 0.5), relwidth=0.091, relheight=0.03)
        self.name.bind('<Configure>', lambda event: work_font(event, 1.7))

        self.H_scale = Label(can, text='0.00 м', width=10, background=can["background"], font=("", 7))
        self.H_scale.place(relx=0.52 + (number * 0.31), rely=0.21 + (number * 0.5), relwidth=0.09, relheight=0.03)
        self.H_scale.bind('<Configure>', lambda event: work_font(event, 1.7))

        self.level = Label(can, text="Степень\nоткрытия", background=can["background"], font=("", 8))
        self.level.place(relx=0.535 + (number * 0.31), rely=0.3 + (number * 0.5), relwidth=0.09, relheight=0.07)
        self.level.bind('<Configure>', lambda event: work_font(event, 4))

        self.Label_m = Label(can, text=f"{self.m}%", font=('', 9), width=4)
        self.Label_m.place(relx=0.55 + (number * 0.306), rely=0.38 + (number * 0.49), relwidth=0.065, relheight=0.038)

        self.B1 = Button(can, text='▼', font=('', 11), command=self.B1)
        self.B1.place(relx=0.52 + (number * 0.306), rely=0.38 + (number * 0.49), relwidth=0.03, relheight=0.038)
        self.B1.bind('<Configure>', lambda event: work_font(event, 1.7))

        self.B2 = Button(can, text='▲', font=('', 11), command=self.B2)
        self.B2.place(relx=0.615 + (number * 0.306), rely=0.38 + (number * 0.49), relwidth=0.03, relheight=0.038)
        self.B2.bind('<Configure>', lambda event: work_font(event, 1.7))

    def B1(self):
        if self.m > 0:
            self.m -= 2.5
            self.Label_m.config(text=f"{self.m}%")

    def B2(self):
        if self.m < 100:
            self.m += 2.5
            self.Label_m.config(text=f"{self.m}%")

    def resize_place(self, W, H):
        self.BAK.configure(image=photo_bak)
        self.V.configure(image=VENT1)
        self.W_can = W
        self.H_can = H

    def delete(self):
        for widget in [self.water, self.V, self.BAK, self.level,
                       self.H_scale, self.Label_m, self.B1, self.B2, self.name]:
            widget.destroy()

    def update_Q_in(self, Q):
        self.Q_in = Q

    def Q_OUT(self):
        return self.Q_out

    def simulation(self):
        if self.m > 0 and self.H > 0:
            self.V.configure(image=VENT2)
            self.BAK.configure(image=photo_bak2)
        else:
            self.V.configure(image=VENT1)
            self.BAK.configure(image=photo_bak)

        self.Q_out = round(((self.m / 100) * sqrt((2 * self.H * 9.82)) * 0.002), accuracy)

        if self.Q_out != 0 or self.Q_in != 0:
            self.H += round((self.Q_in - self.Q_out) / self.S, accuracy)

        self.H_scale.config(text=f"{round(float(self.H), 2)} м")

        if self.H / self.h > 0.01:
            k = 0.36 * (self.H / self.h)
            a = self.pil_water.resize((550, int(k * self.H_can)))
            self.water_image = ImageTk.PhotoImage(a)
            self.water.configure(image=self.water_image)
            self.water.image = self.water_image


def FKB1():
    global Bak2
    if len(Bak2) == 1:
        Bak2[0].delete()
        Bak2.pop()


def FKB2():
    global Bak2
    if len(Bak2) == 0:
        b = Bak(can, 1)
        Bak2.append(b)


def IMAGES(W, H):
    global photo_bak, VENT1, VENT2, VENT_LABEL, water, photo_bak2

    pil_image = Image.open(resource_path("photo/BAK1.png"))
    pil_image = pil_image.resize((int(W * 0.1483), int(H * 0.4694)))
    photo_bak = ImageTk.PhotoImage(pil_image)

    pil_image = Image.open(resource_path("photo/BAK2.png"))
    pil_image = pil_image.resize((int(W * 0.1483), int(H * 0.4694)))
    photo_bak2 = ImageTk.PhotoImage(pil_image)

    pil_image = Image.open(resource_path("photo/V1.png"))
    pil_image = pil_image.resize((int(W * 0.1796), int(H * 0.0857)))
    VENT1 = ImageTk.PhotoImage(pil_image)

    pil_image = Image.open(resource_path("photo/V2.png"))
    pil_image = pil_image.resize((int(W * 0.1796), int(H * 0.0857)))
    VENT2 = ImageTk.PhotoImage(pil_image)

    VENT_LABEL = Label(can, image=VENT1, borderwidth=0, anchor=SW)
    VENT_LABEL.place(relx=0.005, rely=0.37 + 0.5, relwidth=0.145, relheight=0.085)


def background_timer(stop_event):
    global count_time
    while not stop_event.is_set():
        count_time.config(text=str(1 + int(count_time.cget("text"))))
        stop_event.wait(1)

def F_pusk():
    global timer_flag
    if timer_flag:
        stop_event_timer.set()
        Button_pusk.config(text="ПУСК")
    else:
        stop_event_timer.clear()
        thread = Thread(target=background_timer, args=(stop_event_timer,))
        thread.daemon = True
        thread.start()
        Button_pusk.config(text="СТОП")
    timer_flag = not timer_flag


def simulation(simulation_event):
    global Bak2
    while not simulation_event.is_set():
        Bak1.update_Q_in(QIN)
        Bak1.simulation()
        if len(Bak2) > 0:
            Bak2[0].update_Q_in(Bak1.Q_OUT())
            Bak2[0].simulation()


def maintain_aspect_ratio(event):
    global WIDTH, HEIGHT, photo_bak, hm, wm, can, rotametr_image_PIL, truba, number_rotametr_photo, rotametr_photo_list, rotametr_label, truba_image2, truba_image

    if event.widget.master:
        return

    if WIDTH != event.width:
        desired_width = event.width
        desired_height = int(event.width * 0.8073)
    elif HEIGHT != event.height:
        desired_height = min(event.height, hm)
        desired_width = int(desired_height * 1.2388)
    else:
        return

    if desired_height > root.winfo_screenheight():
        desired_height = root.winfo_screenheight() - 10
        desired_width = int(desired_height * 1.2388)

    if event.width != desired_width or event.height != desired_height:
        event.widget.geometry(f'{desired_width}x{desired_height}')
        desired_width = min(desired_width, wm)
        desired_height = min(desired_height, hm)

        if desired_height / desired_width > 490 / 607:
            desired_width = int(desired_height * 1.2388) + 1

        can.config(width=desired_width, height=desired_height)
        can.width = desired_width
        can.height = desired_height

        rotametr_photo_list = []
        for i in range(41):
            rotametr_image_PIL = Image.open(resource_path(f"photo/rotametr/{i}.png"))
            rotametr_image = rotametr_image_PIL.resize((int(desired_width * 0.11), int(desired_height * 0.87)))
            photo = ImageTk.PhotoImage(rotametr_image)
            rotametr_photo_list.append(photo)

        number_rotametr_photo = max(0, min(number_rotametr_photo, len(rotametr_photo_list) - 1))
        rotametr_label = Label(can, image=rotametr_photo_list[number_rotametr_photo], borderwidth=0)
        rotametr_label.place(relx=0.15, rely=0.095, relwidth=0.1, relheight=0.85)
        rotametr_label.image = rotametr_photo_list[number_rotametr_photo]

        truba_PIl = truba.resize((int(desired_width * 0.222), int(desired_height * 0.0654)))
        truba_image = ImageTk.PhotoImage(truba_PIl)

        truba_PIl2 = truba2.resize((int(desired_width * 0.222), int(desired_height * 0.0654)))
        truba_image2 = ImageTk.PhotoImage(truba_PIl2)

        truba_label.configure(image=truba_image)
        truba_label.image = truba_image

        IMAGES(desired_width, desired_height)
        Bak1.resize_place(desired_width, desired_height)
        if len(Bak2) > 0:
            Bak2[0].resize_place(desired_width, desired_height)

        return "break"


# Инициализация главного окна
root = Tk()
root.title('Эмулятор стенда лабораторной работы №7')
root.state('zoomed')
root.resizable(width=False, height=False)

# Основные переменные
accuracy = 6
Bak2 = []
simulation_event = Event()
stop_event_timer = Event()
timer_flag = False
QIN = 0.0
Qm = 0.0
number_rotametr_photo = 0

# Создание холста
can = Canvas(root, width=605, height=490, bg='lightgray')
can.configure(bg="#b5e61d")

hm = root.winfo_screenheight() - 65
wm = int(hm * 1.2388)

# Таймер (секундомер)
timer = Label(can, text='Секундомер', background="#696969", foreground='white', font=("", 8))
timer.place(relx=0.7, rely=0.042, relwidth=0.12, relheight=0.042)
timer.bind('<Configure>', lambda event: work_font(event, 2.2))

count_time = Label(can, text='0', width=7, anchor="w", background="black", foreground='white', font=("", 10))
count_time.place(relx=0.7, rely=0.082, relwidth=0.12, relheight=0.042)
count_time.bind('<Configure>', lambda event: work_font(event, 1.6))

Button_pusk = Button(can, text='ПУСК', background='white', width=6, command=F_pusk, font=("", 12))
Button_pusk.place(relx=0.7, rely=0.124, relwidth=0.12, relheight=0.062)
Button_pusk.bind('<Configure>', lambda event: work_font(event, 1.6))

Button_sbros = Button(can, text='СБРОС', background='white', width=6, command=lambda: count_time.config(text='0'),
                      font=("", 12))
Button_sbros.place(relx=0.7, rely=0.19, relwidth=0.12, relheight=0.062)
Button_sbros.bind('<Configure>', lambda event: work_font(event, 2))

# Загрузка изображений
truba = Image.open(resource_path("photo/truba.png"))
truba_PIl = truba.resize((int(607 * 0.156), int(490 * 0.03)))
truba_image = ImageTk.PhotoImage(truba_PIl)

truba2 = Image.open(resource_path("photo/truba2.png"))
truba_PIl2 = truba2.resize((int(607 * 0.156), int(490 * 0.03)))
truba_image2 = ImageTk.PhotoImage(truba_PIl2)

truba_label = Label(can, image=truba_image, borderwidth=0)
truba_label.place(relx=0.15, rely=0.03, relwidth=0.22, relheight=0.065)

rotametr_water = Image.open(resource_path("photo/water.png"))
rotametr_water_PIL = rotametr_water.resize((86, 1))
rotametr_water_img = ImageTk.PhotoImage(rotametr_water_PIL)
RWIL = Label(can, image=rotametr_water_img, borderwidth=0, anchor=S)

rotametr = Label(can, text=f'Показания\nротаметра\n{QIN} м³/с', font=("", 8))
rotametr.place(relx=0.02, rely=0.03, relwidth=0.11, relheight=0.1)
rotametr.bind('<Configure>', lambda event: work_font(event, 5))

# Кнопки управления
Button_1 = Button(can, text='▼', font=('', 11), command=lambda: update_Q('-'))
Button_1.place(relx=0.025, rely=0.327 + 0.5, relwidth=0.03, relheight=0.038)
Button_1.bind('<Configure>', lambda event: work_font(event, 1.7))

Button_2 = Button(can, text='▲', font=('', 11), command=lambda: update_Q('+'))
Button_2.place(relx=0.119, rely=0.327 + 0.5, relwidth=0.03, relheight=0.038)
Button_2.bind('<Configure>', lambda event: work_font(event, 1.7))

Q = Label(can, text=f"{Qm}%", font=('', 9), width=4)
Q.place(relx=0.053, rely=0.327 + 0.5, relwidth=0.065, relheight=0.038)

# Элементы управления баками
Label_KOL_Bak = Label(can, text='Кол.во ёмкостей:', background=can["background"], font=("", 8))
Label_KOL_Bak.place(relx=0.83, rely=0.042, relwidth=0.157, relheight=0.03)
Label_KOL_Bak.bind('<Configure>', lambda event: work_font(event, 1.7))

kol_baks = StringVar(value='1')
kol_baks_1 = ttk.Radiobutton(can, text='1 ёмкость', value='1', variable=kol_baks, command=FKB1)
kol_baks_1.place(relx=0.83, rely=0.08, relwidth=0.155, relheight=0.04)

kol_baks_2 = ttk.Radiobutton(can, text='2 ёмкости', value='2', variable=kol_baks, command=FKB2)
kol_baks_2.place(relx=0.83, rely=0.12, relwidth=0.155, relheight=0.042)

style = ttk.Style()
style.configure("TRadiobutton", font=('', 10))

# Инициализация баков
IMAGES(607, 490)
Bak1 = Bak(can, 0)

# Автоматический запуск симуляции
simulation_event.clear()
simulation_thread = Thread(target=simulation, args=(simulation_event,))
simulation_thread.daemon = True
simulation_thread.start()

# Автоматический запуск таймера
stop_event_timer.clear()
timer_thread = Thread(target=background_timer, args=(stop_event_timer,))
timer_thread.daemon = True
timer_thread.start()
Button_pusk.config(text="СТОП")

# Настройка главного окна
WIDTH, HEIGHT = 607, 490
root.geometry(f'{WIDTH}x{HEIGHT}')
root.minsize(607, 490)
root.maxsize(root.winfo_screenwidth(), root.winfo_screenheight())

can.pack()

# Установка иконки
myappid = 'mycompany.myproduct.subproduct.version'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
root.wm_iconbitmap(resource_path('lab.ico'))

root.protocol("WM_DELETE_WINDOW", root.destroy)
root.bind('<Configure>', maintain_aspect_ratio)

# Убираем обработчик события Map, так как он больше не нужен
# root.bind("<Map>", lambda event: None)

root.mainloop()