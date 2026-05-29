import cv2
import numpy as np
import mss
import time
import pyautogui

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# Область захвата экрана
GAME_REGION = {
    "top": 450,                                                
    "left": 120,
    "width": 700,
    "height": 230 
}

sct = mss.mss()
    
# Задержка перед стартом и нажатие пробела для начала игры
time.sleep(2) 
pyautogui.press("space")

# Скорость движения зон (пикселей в секунду)
SHIFT_RATE_S = 3.0
SHIFT_RATE_Z = 2.8 
SHIFT_RATE_P = 1.3
 
# Вертикальные границы зон
STRIP_Y1, STRIP_Y2 = 145, 180
STRIP_X1, STRIP_X2 = 100, 162   

# Координаты зоны птеродактиля
PTER_Y1, PTER_Y2 = 106 , 111       
PTER_X1, PTER_X2 = 120, 158        
    

start_time = time.time() 
 
# Переменные для расчёта дистанций 
                                         
while True:          
    elapsed = time.time() - start_time

    if elapsed >= 8.7:
        STRIP_X2 = 210
        PTER_X2 = 160    
 
    if elapsed >= 24 :
        STRIP_X2 = 280
        PTER_X2 = 180
 
    if elapsed >= 41:
        STRIP_X2 = 375   
        PTER_X2 = 210      
   
    # Захват кадра и бинаризация (тёмное → белое)
    gray = cv2.cvtColor(np.array(sct.grab(GAME_REGION)), cv2.COLOR_BGRA2GRAY)
    _, thresh = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY_INV)
 
    # Выделение зон на кадре и подсчёт белых пикселей
    obstacle_zone = thresh[STRIP_Y1:STRIP_Y2, STRIP_X1 : STRIP_X2]
    pxPter_zone = thresh[PTER_Y1:PTER_Y2, PTER_X1 : PTER_X2]
                     
    pixels = cv2.countNonZero(obstacle_zone)      
    pxPter = cv2.countNonZero(pxPter_zone)

         
    # Обычный прыжок по основной полоске
    if pixels > 50: 
        pyautogui.keyDown("space")    


    # Приседание под птеродактилем
    if pxPter > 5:
        pyautogui.keyDown("down")
        time.sleep(0.30) 
        pyautogui.keyUp("down") 
            
    # Отрисовка зон для отладки
    debug = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)                                                                     
             
    cv2.rectangle(debug, (STRIP_X1, STRIP_Y1), (STRIP_X2, STRIP_Y2), (0,0,255), 2)
    cv2.rectangle(debug, (PTER_X1, PTER_Y1), (PTER_X2, PTER_Y2), (0, 255, 255), 2)
    cv2.imshow("Obstacle Detection", debug)                          

    # Выход из цикла
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  
cv2.destroyAllWindows() 
