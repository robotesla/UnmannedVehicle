#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import cv2 as cv
import time

cap = cv.VideoCapture(0) #поток с камеры

uh = 190 #создаем переменные для фильтра HSV
us = 255
uv = 255
lh = 120
ls = 100
lv = 100

lower_hsv = np.array([lh,ls,lv]) #пакуем эти переменные в массив
upper_hsv = np.array([uh,us,uv])

window_name = "detector_calibration" #название окна
cv.namedWindow(window_name) #создаем окно

def nothing(x): #коллбек функция на изменение положения ползунка
    print("Trackbar value: " + str(x))
    pass

# создаем трекбары для Upper HSV
cv.createTrackbar('UpperH',window_name,0,255,nothing)
cv.setTrackbarPos('UpperH',window_name, uh)

cv.createTrackbar('UpperS',window_name,0,255,nothing)
cv.setTrackbarPos('UpperS',window_name, us)

cv.createTrackbar('UpperV',window_name,0,255,nothing)
cv.setTrackbarPos('UpperV',window_name, uv)

# создаем трекбары Lower HSV
cv.createTrackbar('LowerH',window_name,0,255,nothing)
cv.setTrackbarPos('LowerH',window_name, lh)

cv.createTrackbar('LowerS',window_name,0,255,nothing)
cv.setTrackbarPos('LowerS',window_name, ls)

cv.createTrackbar('LowerV',window_name,0,255,nothing)
cv.setTrackbarPos('LowerV',window_name, lv)


# создаем SimpleBlobdetector с параметрами по умолчанию.     
detector = cv.SimpleBlobDetector_create()


# начинаем
while(True):
    # захватываем изображение (frame) из видеопотока
    ret, frame = cap.read()


    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)     #преобразуем изображение в ХСВ
    mask = cv.inRange(hsv, lower_hsv, upper_hsv)   #применяем фильтр ХСВ и записываем результат в изображение (mask)
   
    #обновляем положение трекбаров и записываем в переменные
    uh = cv.getTrackbarPos('UpperH',window_name)   
    us = cv.getTrackbarPos('UpperS',window_name)
    uv = cv.getTrackbarPos('UpperV',window_name)
    lh = cv.getTrackbarPos('LowerH',window_name)
    ls = cv.getTrackbarPos('LowerS',window_name)
    lv = cv.getTrackbarPos('LowerV',window_name)
    upper_hsv = np.array([uh,us,uv])
    lower_hsv = np.array([lh,ls,lv])

    # находим только ВНЕШНИЕ контуры  на изображении (mask), внтуренние контуры отбрасываются
    _, contours0, hierarchy = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # создаем пустое изображение (читай пустой массив 5х5х3)
    crop_ellipse = np.zeros((5,5,3), np.uint8)

    for cnt in contours0: #проходимся по всем найденным контурам
        if len(cnt)>4:    #если контур содержит больше четырех точек (не мелкий)
            ellipse = cv.fitEllipse(cnt) #то ищем в контуре эллипс
            # print(ellipse)
            if ellipse: # если эллипс найден
                x = ellipse[0][0] #координата центра эллипса по х
                y = ellipse[0][1] #координата центра эллипса по у
                w = ellipse[1][0] #ширина эллипса
                h = ellipse[1][1] #высота эллипса
                #angle = ellipse[2] #угол наклона (в программе не используется)

                #ratio_ellipse = соотношение сторон эллипса, помогает отбросить вытянутые эллипсы, которые явно не являются знаками
                #ellipse[1] это массив из двух значений ширины и высоты, поэтому максимальное значение массива делится на минимальное, что из этого будет шириной или высотой - значения не имеет
                ratio_ellipse = max(ellipse[1])/(min(ellipse[1])+0.1) # + 0.1 чтобы избежать деления на 0

                #тут начинается веселье
                if (w>10 and h>10 and ratio_ellipse<1.3): #если эллипс больше 20х20 пикселей и не очень вытянутый
                    crop_ellipse = mask[int(y-(h/2)-5):int(y+(h/2)+5), int(x-(w/2)-5):int(x+(w/2)+5)] #создаем обрезанное изображение маски (crop_ellipse), вырезается из чб маски в месте найденного эллипса
                    crop_ellipse = cv.medianBlur(crop_ellipse,1) #немного замыливаем маску

                    if not crop_ellipse is None: #если обрезание удалось
                        __, contours_box, hierarchy_box = cv.findContours(255-crop_ellipse.copy(), cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE) #255-crop_ellipse.copy() инвертируем обрезанную маску и ищем на ней контуры, опять
                        for i in contours_box: #проходимся по найденным контурам
                            if len(i)>6: #если контур содержит больше 6 точек (не мелкий)
                                rect = cv.minAreaRect(i) #пытаемся найти и вписать прямоугольник
                                if (rect[1][0]>5 and rect[1][1]>5): #если размеры прямоугольника чуть больше чем ничто
                                    x_box = rect[0][0] #координата х центра прямоугольника
                                    y_box = rect[0][1] #координата у центра прямоугольника
                                    w_box = rect[1][0] #ширина прямоугольника
                                    h_box = rect[1][1] #высота прямоугольника
                                    x_delta = abs(x_box - w/2 - 5) #разница по координате х между найденным эллипсом и найденным в нем прямоугольнике
                                    y_delta = abs(y_box - h/2 - 5) #разница по координате х между найденным эллипсом и найденным в нем прямоугольнике
                                    ratio_box = max(rect[1])/min(rect[1]) # вычисляем соотношение сторон найденного прямоугольника по аналогии с эллипсом 
                                    if (ratio_box>3 and x_delta<10 and y_delta<10): #если прямоугольник вытянутый и находится не дальше чем 10 пикселей от центра эллипса
                                        print("find_stop")
                                        box = cv.boxPoints(rect) #ищем координаты прямоугольника
                                        box = np.intc(box) #и округляем их
                                        
                                        for p in range(4):#двигаем координаты на свое место
                                            box[p][0] += x-w/2-5 
                                            box[p][1] += y-h/2-5

                                        cv.drawContours(frame,[box],0,(255,0,0),2) #рисуем прямоугольник
                                        cv.ellipse(frame,ellipse,(0,255,0),2)      #и сразу тот самый эллипс, в котором нашелся нужный прямоугольник в нужно месте
                                        cv.imshow("ellipse",255-crop_ellipse) #выводим обрезанную по эллипсу маску с инверсией чб
                            
                    else:
                        #если обрезание не удалось, то рисуем пустоту
                        crop_ellipse = np.zeros((500,500,3), np.uint8) 
                        continue #и переходим к следующему эллипсу

            else:
                #если эллипс не найден, то тоже рисуем пустоту
                crop_ellipse = np.zeros((500,500,3), np.uint8) 
                continue #и ищем следующий эллипс
            

    cv.imshow(window_name,mask) #выводим окно с настройками ХСВ и большую маску   
    cv.imshow("original",frame) #рисуем исходное изображение
    
    
    if cv.waitKey(1) & 0xFF == ord('q'): #если нажата кнопка q на клавиатуре, то завершить цикл
        break

cap.release() #остановка видеопотока
cv.destroyAllWindows() #закрываем все окна