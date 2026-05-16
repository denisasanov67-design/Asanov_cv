import cv2
import numpy as np
import mss
import time
import pyautogui

# Область захвата экрана
GAME_REGION = {
    "top": 370,
    "left": 120,
    "width": 700,
    "height": 230
}

sct = mss.mss()
    
# Задержка перед стартом и нажатие пробела для начала игры
time.sleep(3) 
pyautogui.press("space")

# Ограничители смещения для каждой группы зон
MAX_SHIFT_S = 140
MAX_SHIFT_P = 55
MAX_SHIFT_Z = 105    
START_X = 142 
STRIP_W = 6  

# Скорость движения зон (пикселей в секунду)
SHIFT_RATE_S = 3.0
SHIFT_RATE_Z = 2.8
SHIFT_RATE_P = 1.3

# Вертикальные границы зон
STRIP_Y1, STRIP_Y2, STRIP_Z = 150, 180, 110         

# Горизонтальные границы дополнительных зон
Z1_X1, Z1_X2 = 105, 238 
Z2_X1, Z2_X2 = 310, 470  

# Параметры зоны мнгновенного прыжка 
PROB_X = 100
PROB_W = 6 
BROB_Y1, BROB_Y2 = STRIP_Y1, STRIP_Y2

# Координаты зоны птеродактиля
PTER_Y1, PTER_Y2 = 113, 120       
PTER_X1, PTER_X2 = 120, 158        
    
start_time = time.time() 
 
# Переменные для расчёта дистанций 

game_speed = 1.0
dist_small = 95
dist_large = 90
dist_group_2small = 75
dist_group_2large = 75
dist_group_3small = 75
dist_group_4mixed = 75
dist_bird_duck = 100  
dist_bird_jump = 95
                                         
while True:          
    elapsed = time.time() - start_time

    # Расчёт скорости игры по таймеру
    if elapsed < 10: time_speed = 1.1
    elif elapsed < 22: time_speed = 2.1
    elif elapsed < 32: time_speed = 3.5
    elif elapsed < 40: time_speed = 4.2
    elif elapsed < 49: time_speed = 4.9
    elif elapsed < 60: time_speed = 5.5
    elif elapsed < 69: time_speed = 6.2
    elif elapsed < 78: time_speed = 8.0
    elif elapsed < 100: time_speed = 8.8
    elif elapsed < 130: time_speed = 9.1
    elif elapsed < 160: time_speed = 9.9
    elif elapsed < 180: time_speed = 10.9
    else: time_speed = 12.0
    
    # Сглаживание скорости и расчёт коэффициента влияния на смещение
    game_speed = game_speed * 0.85 + time_speed * 0.265
    factor = 1 + max(0, game_speed - 1) * 0.2

    # Расчёт текущего смещения для каждой зоны с ограничителями
    current_shift_s = min(MAX_SHIFT_S, max(0, int((elapsed - 10) * SHIFT_RATE_S)))
    current_shift_z = min(MAX_SHIFT_Z , max(0,int((elapsed - 10) * SHIFT_RATE_Z))) 
    current_shift_p = min(MAX_SHIFT_P , max(0,int((elapsed - 10) * SHIFT_RATE_P))) 

    # Обновление координат основной полоски и зоны птера
    if elapsed > 6:
        pt_x1 = PTER_X1 + current_shift_s
        pt_x2 = PTER_X2 + current_shift_s
        strip_x = START_X + current_shift_s    
    else:
        pt_x1 = PTER_X1
        pt_x2 = PTER_X2 
        strip_x = START_X          
    
    # Обновление координаты зоны PROB
    if elapsed > 15:
        pr_x = PROB_X + current_shift_p
    else:
        pr_x = PROB_X

    # Обновление координат зон 1 и 2
    if elapsed > 17:
         z1_x1 = Z1_X1 + int(0.65  *current_shift_z) 
         z1_x2 = Z1_X2 + current_shift_z
         z2_x1 = Z2_X1 + current_shift_z 
         z2_x2 = Z2_X2 + current_shift_z
    else: 
         z1_x1 = Z1_X1 
         z1_x2 = Z1_X2 
         z2_x1 = Z2_X1 
         z2_x2 = Z2_X2 

    # Захват кадра и бинаризация (тёмное → белое)
    screenshot = sct.grab(GAME_REGION)
    img = np.array(screenshot)
    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(
        gray,                            
        90, 
        255,    
        cv2.THRESH_BINARY_INV
    )

    # Выделение зон на кадре и подсчёт белых пикселей
    obstacle_zone = thresh[STRIP_Y1:STRIP_Y2, strip_x : strip_x + STRIP_W]
    zone1 = thresh[STRIP_Y1:STRIP_Y2, z1_x1 : z1_x2]
    zone2 = thresh[STRIP_Z:STRIP_Y2, z2_x1 : z2_x2]
    pxPter_zone = thresh[PTER_Y1:PTER_Y2, pt_x1 : pt_x2]
    prob_zone = thresh[STRIP_Y1:STRIP_Y2, pr_x : pr_x + PROB_W]
                     
    pixels = cv2.countNonZero(obstacle_zone)      
    pxZone1 = cv2.countNonZero(zone1)
    pxZone2 = cv2.countNonZero(zone2)
    pxPter = cv2.countNonZero(pxPter_zone)
    pxProb = cv2.countNonZero(prob_zone)


    # Логика прыжков и приседания

    # Двойной прыжок при обнаружении препятствий в двух зонах
    if pxZone1 > 50 and pxZone2 > 50:
        pyautogui.keyDown("space")
        time.sleep(0.04)  
        pyautogui.keyUp("space")
        time.sleep(0.05)  


    # Мгновенный прыжок по зоне PROB
    if pxProb > 4:
         pyautogui.keyDown("space")
         time.sleep(0.0)
         pyautogui.keyUp("space")
         
    # Обычный прыжок по основной полоске
    if pixels > 4: 
        pyautogui.keyDown("space")    
        time.sleep(0.05) 
        pyautogui.keyUp("space")

    # Приседание под птеродактилем
    if pxPter > 4:
        pyautogui.keyDown("down")
        time.sleep(0.25) 
        pyautogui.keyUp("down") 
            
    # Отрисовка зон для отладки
    debug = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)                                                                     
             
    cv2.rectangle(debug, (strip_x, STRIP_Y1), (strip_x + STRIP_W, STRIP_Y2), (0,0,255), 2)
    cv2.rectangle(debug, (z1_x1, STRIP_Y1), (z1_x2, STRIP_Y2), (0, 255, 0), 2)
    cv2.rectangle(debug, (z2_x1, STRIP_Z), (z2_x2, STRIP_Y2), (255, 0, 0), 2)
    cv2.rectangle(debug, (pt_x1, PTER_Y1), (pt_x2, PTER_Y2), (0, 255, 255), 2)
    cv2.rectangle(debug, (pr_x, BROB_Y1), (pr_x + PROB_W, BROB_Y2), (255, 255, 0), 2)
         
    cv2.imshow("Obstacle Detection", debug)                          

    # Выход из цикла
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  

cv2.destroyAllWindows()