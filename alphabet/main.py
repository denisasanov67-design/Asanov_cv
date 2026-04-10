import numpy as np
import matplotlib.pyplot as plt 
from skimage.measure import label, regionprops
from skimage.io import imread

def count_holes(region):
    shape = region.image.shape
    new_image = np.zeros ((shape[0]+2, shape[1]+2))
    new_image[1:-1, 1:-1] = region.image
    new_image = np.logical_not(new_image)
    labeled = label(new_image)
    return np.max(labeled) - 1

def classificator(region):
    holes = count_holes(region)
    if holes == 2:
        vlines = (np.sum(region.image,
                         0) == region.image.shape[0]).sum()
        vlines = vlines / region.image.shape[1]

        if vlines > 0.2:
            return "B"
        else:
            return "8"
        
    elif holes == 1: # A,O,P,D
        if region.eccentricity > 0.6:
            return "0"
        else:
            height, width = region.image.shape
            aspect_ratio = height/width # соотношение высоты к ширине 

            if aspect_ratio > 1.2:
                return "P"
            elif aspect_ratio < 0.8:
                return "D"
            else:
                return "A"
    
    else:
        if region.image.sum() == region.image.size:
            return "-"
        
        shape = region.image.shape
        aspect = np.min(shape) / np.max(shape)
        if aspect>0.9:
            return "*"
        vlines = (np.sum(region.image, 0) == region.image.shape[0]).sum()
        hlines = (np.sum(region.image, 1) == region.image.shape[1]).sum()

        if vlines > 0 and hlines > 0:
            return "1"
        
        labeled = label(np.logical_not(region.image))
        bays = 0
        for r in regionprops(labeled):
            if r.area > 3:
                bays += 1
        if bays == 2:
            return "/"
        elif bays == 4:
            return "X"
        elif bays == 5:
            return "W"
    return "?"

image = plt.imread("symbols.png")[:,:,-1]
abinary = image > 0 
alabeled = label(abinary)
print(np.max(alabeled))
aprops = regionprops(alabeled)

res = {}
plt.figure(figsize = (5,7))

for region in aprops:
    symbol = classificator(region)
    if symbol not in res:
        res[symbol] = 0
    res[symbol] += 1

for symbol in res:
    print(f"{symbol} = {res[symbol]}")
