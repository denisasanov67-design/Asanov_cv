import matplotlib.pyplot as plt
import numpy as np

labeled = np.zeros((16,16))
labeled[4:,:4] = 1


labeled[3:10,8:] =2
labeled[[3,4,3], [8,8,9]] = 0
labeled[[8,9,9], [8,8,9]] = 0
labeled[[3,4,3], [-2,-1,-1]] = 0
labeled[[9,8,9], [-2,-1,-1]] = 0

plt.imshow(labeled)
plt.show()