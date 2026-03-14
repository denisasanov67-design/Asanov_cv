import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label
from skimage.morphology import binary_opening


image = np.load("wires3.npy")
struct = np.ones((3, 1))
processed = binary_opening(image, struct)
labeled = label(image)

print("Количество проводов:", np.max(labeled))

for num in range(1, np.max(labeled) + 1):

    mask = labeled == num
    wire_processed = processed * mask
    parts = label(wire_processed)
    count = np.max(parts)

    if count <= 1:
        print(f"Провод {num}: целый")
    else:
        print(f"Провод {num}: порван на {count} частей")


plt.subplot(121)
plt.title("Original")
plt.imshow(image)

plt.subplot(122)
plt.title("Processed")
plt.imshow(processed)

plt.show()