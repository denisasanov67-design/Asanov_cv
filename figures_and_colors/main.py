import cv2
import numpy as np


img = cv2.imread("balls_and_rects.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

blur = cv2.GaussianBlur(gray, (5, 5), 0)

edges = cv2.Canny(blur, 50, 150)


contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

circles = 0
quadrilaterals = 0

circle_colors = []
quadrilateral_colors = []


def get_color_name(b, g, r):

    max_val = max(r, g, b)
    min_val = min(r, g, b)

    if max_val < 50:
        return "Черный"
    if min_val > 200:
        return "Белый"

    if max_val == r and r > g + 30 and r > b + 30:
        if g > 100 and b < 100:
            return "Оранжевый"
        return "Красный"

    if max_val == g and g > r + 30 and g > b + 30:
        if r > 100:
            return "Салатовый"
        return "Зеленый"

    if max_val == b and b > r + 30 and b > g + 30:
        if r > 100:
            return "Фиолетовый"
        return "Синий"

    if r > 150 and g > 150 and b < 100:
        return "Желтый"

    if r > 150 and b > 150 and g < 100:
        return "Пурпурный"

    if g > 150 and b > 150 and r < 100:
        return "Голубой"

    if r > 150 and g > 100 and g < 150 and b < 100:
        return "Коричневый"

    if r > 150 and g > 150 and b > 150:
        return "Светло-серый"

    if r < 100 and g < 100 and b < 100:
        return "Темно-серый"

    if abs(r - g) < 30 and abs(g - b) < 30:
        if r > 100:
            return "Серый"

    return "Другой"


for cnt in contours:

    epsilon = 0.04 * cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon, True)

    mask = np.zeros(gray.shape, np.uint8)
    cv2.drawContours(mask, [cnt], -1, 255, -1)


    mean_color = cv2.mean(img, mask=mask)
    b, g, r = int(mean_color[0]), int(mean_color[1]), int(mean_color[2])
    color_name = get_color_name(b, g, r)


    if len(approx) == 4:
        quadrilaterals += 1
        quadrilateral_colors.append(color_name)


    area = cv2.contourArea(cnt)
    perimeter = cv2.arcLength(cnt, True)

    if perimeter != 0:
        circularity = 4 * 3.14159 * area / (perimeter * perimeter)


        if circularity > 0.8:
            circles += 1
            circle_colors.append(color_name)

print("Круги:", circles)
print("Четырёхугольники:", quadrilaterals)
print("\nЦвета кругов:")
for color in sorted(set(circle_colors)):
    print(f"  {color}: {circle_colors.count(color)}")
print("\nЦвета четырёхугольников:")
for color in sorted(set(quadrilateral_colors)):
    print(f"  {color}: {quadrilateral_colors.count(color)}")