#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import cv2 as cv
import time
import sys,os

cap = cv.VideoCapture(0) #поток с камеры

template_img = [] 
for i in range(5):
    print(os.path.abspath(os.path.dirname(sys.argv[0])) + "/template" + str(i) + ".png")
    template_img.append(cv.imread(os.path.abspath(os.path.dirname(sys.argv[0])) + "/template" + str(i) + ".png",1))
    
# right_img = cv.imread('/home/q/catkin_ws/src/traffic_detect/scripts/template2.png',1)
for i in range(len(template_img)):
    print(len(template_img))
    template_img[i] = 255-cv.inRange(template_img[i], np.array([100,80,80]), np.array([255,255,255]))
    # template_img[1] = 255-cv.inRange(template_img[1], np.array([100,80,80]), np.array([255,255,255]))

uh = 132 #создаем переменные для фильтра HSV
us = 255
uv = 255
lh = 85
ls = 40
lv = 40
thr_f = 70
thr_l = 70
thr_r = 70
thr_fl = 70
thr_fr = 70

lower_hsv = np.array([lh,ls,lv]) #пакуем эти переменные в массив
upper_hsv = np.array([uh,us,uv])

window_name = "detector_calibration" #название окна
cv.namedWindow(window_name) #создаем окно

window_thresholds = "thresholds" #название окна
cv.namedWindow(window_thresholds) #создаем окно

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

cv.createTrackbar('forward',window_thresholds,0,100,nothing)
cv.setTrackbarPos('forward',window_thresholds, thr_f)
cv.createTrackbar('left',window_thresholds,0,100,nothing)
cv.setTrackbarPos('left',window_thresholds, thr_l)
cv.createTrackbar('right',window_thresholds,0,100,nothing)
cv.setTrackbarPos('right',window_thresholds, thr_r)
cv.createTrackbar('forward_left',window_thresholds,0,100,nothing)
cv.setTrackbarPos('forward_left',window_thresholds, thr_fl)
cv.createTrackbar('forward_right',window_thresholds,0,100,nothing)
cv.setTrackbarPos('forward_right',window_thresholds, thr_fr)

# создаем SimpleBlobdetector с параметрами по умолчанию.     
detector = cv.SimpleBlobDetector_create()

count = 0

def sortByLength(inputStr):
        return len(inputStr)


# начинаем
while(True):
    # захватываем изображение (frame) из видеопотока
    ret, frame = cap.read()


    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)     #преобразуем изображение в ХСВ
    # hsv = cv.blur(hsv,(5,5))

    mask = cv.inRange(hsv, lower_hsv, upper_hsv)   #применяем фильтр ХСВ и записываем результат в изображение (mask)

    #обновляем положение трекбаров и записываем в переменные
    uh = cv.getTrackbarPos('UpperH',window_name)   
    us = cv.getTrackbarPos('UpperS',window_name)
    uv = cv.getTrackbarPos('UpperV',window_name)
    lh = cv.getTrackbarPos('LowerH',window_name)
    ls = cv.getTrackbarPos('LowerS',window_name)
    lv = cv.getTrackbarPos('LowerV',window_name)
    thr_f = cv.getTrackbarPos('forward',window_thresholds)
    thr_l = cv.getTrackbarPos('left',window_thresholds)
    thr_r = cv.getTrackbarPos('right',window_thresholds)
    thr_fl = cv.getTrackbarPos('forward_left',window_thresholds)
    thr_fr = cv.getTrackbarPos('forward_right',window_thresholds)
    upper_hsv = np.array([uh,us,uv])
    lower_hsv = np.array([lh,ls,lv])

    # находим только ВНЕШНИЕ контуры  на изображении (mask), внтуренние контуры отбрасываются
    _, contours0, hierarchy = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # создаем пустое изображение (читай пустой массив 5х5х3)
    crop_ellipse = np.zeros((5,5,3), np.uint8)
    if contours0 == None:
        continue

    results = [[],[],[],[],[]]
    # print(results)
    contours0 = sorted(contours0,reverse=True,key=sortByLength)
    for cnt in contours0: #проходимся по всем найденным контурам
        if len(cnt)>10:    #если контур содержит больше четырех точек (не мелкий)
            ellipse = cv.fitEllipse(cnt) #то ищем в контуре эллипс
            # print(ellipse)
            if ellipse: # если эллипс найден
                x = int(ellipse[0][0]) #координата центра эллипса по х
                y = int(ellipse[0][1]) #координата центра эллипса по у
                w = int(ellipse[1][0]) #ширина эллипса
                h = int(ellipse[1][1]) #высота эллипса
                #angle = ellipse[2] #угол наклона (в программе не используется)

                #ratio_ellipse = соотношение сторон эллипса, помогает отбросить вытянутые эллипсы, которые явно не являются знаками
                #ellipse[1] это массив из двух значений ширины и высоты, поэтому максимальное значение массива делится на минимальное, что из этого будет шириной или высотой - значения не имеет
                ratio_ellipse = max(ellipse[1])/(min(ellipse[1])+0.1) # + 0.1 чтобы избежать деления на 0

                #тут начинается веселье
                if (w>20 and h>20 and ratio_ellipse<1.3): #если эллипс больше 20х20 пикселей и не очень вытянутый
                    crop_ellipse = mask[int(y-(h/2)-(h*0.6)):int(y+(h/2)+(h*0.6)), int(x-(w/2)-(w*0.6)):int(x+(w/2)+(w*0.6))] #создаем обрезанное изображение маски (crop_ellipse), вырезается из чб маски в месте найденного эллипса
                    # crop_ellipse = cv.medianBlur(crop_ellipse,1) #немного замыливаем маску
                    if np.count_nonzero(crop_ellipse): #если обрезание удалось
                        
                        for t in template_img:
                            s = int(min(crop_ellipse.shape[0],crop_ellipse.shape[1])*0.6)
                            img_temp = cv.resize(t,(s,s))

                            res_img = cv.matchTemplate(crop_ellipse,img_temp,cv.TM_CCOEFF_NORMED)
                            res_num = np.where( res_img >= thr_f/100.0)

                            if np.any(res_num):
                            # print("find!")
                                r = [len(res_num[0]),template_img.index(t),ellipse]
                                results[template_img.index(t)].append(r)
                            # cv.ellipse(frame,ellipse,(0,255,0),2) 
                            
                            # cv.imshow("ellipse",crop_ellipse)
                            # cv.imshow("forward_img",forward_img_temp)
                            # cv.imshow("match",res_forward_img)

                        else:
                            pass
                            # print("empty")

                    else:
                        #если обрезание не удалось, то рисуем пустоту
                        crop_ellipse = np.zeros((500,500,3), np.uint8) 
                        continue #и переходим к следующему эллипсу

                else:
                    #если обрезание не удалось, то рисуем пустоту
                    crop_ellipse = np.zeros((500,500,3), np.uint8) 
                    continue #и переходим к следующему эллипсу
            else:
                #если эллипс не найден, то тоже рисуем пустоту
                crop_ellipse = np.zeros((500,500,3), np.uint8) 
                continue #и ищем следующий эллипс
        # else:
            # break
    

    # print(len(results[0]))

    if results:
        for i in results:
            # for e in i:
            #     cv.ellipse(frame,e[2],(0,255,0),2)
            #     cv.putText(frame,str(e[0]),(int(e[2][0][0]),int(e[2][0][1])),cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),1, cv.LINE_AA)

            results_r = zip(*i[::-1])
            try:
                # print(results_r)
                num_fin = results_r[0].index(max(results_r[0]))
                cv.ellipse(frame,results_r[2][num_fin],(0,0,255),2)
                cv.putText(frame,str(results_r[1][num_fin]),(int(results_r[2][num_fin][0][0]),int(results_r[2][num_fin][0][1])),cv.FONT_HERSHEY_SIMPLEX,1,(0,0,255),1, cv.LINE_AA)
            except:
                pass

    cv.imshow(window_name,mask) #выводим окно с настройками ХСВ и большую маску   
    cv.imshow("original",frame) #рисуем исходное изображение
    
    if cv.waitKey(1) & 0xFF == ord('q'): #если нажата кнопка q на клавиатуре, то завершить цикл
        break

cap.release() #остановка видеопотока
cv.destroyAllWindows() #закрываем все окна