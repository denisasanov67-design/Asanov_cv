import numpy as np
import matplotlib.pyplot as plt
import glob as gl


def centroid(labeled, label = 1):
    x,y = np.where(labeled == label)
    return np.mean(x), np.mean(y)

files = sorted(gl.glob('h_*.npy'))

xcorr = []
ycorr = []

for f in files:
    img = np.load(f)
    cy, cx = centroid(img)
    xcorr.append(cx)
    ycorr.append(cy)

plt.figure()
plt.plot(xcorr,ycorr, color = "green")
plt.grid(True)
plt.axis('equal')
plt.legend()
plt.show()
