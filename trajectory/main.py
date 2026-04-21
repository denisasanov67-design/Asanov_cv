import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
from pathlib import Path
from scipy.optimize import linear_sum_assignment

def load_images(folder):
    files = sorted(Path(folder).glob("*.npy"))
    return [(np.load(f) > 0).astype(int) for f in files]

def get_centroids(img):
    labeled = label(img)
    return [r.centroid[::-1] for r in regionprops(labeled)]

def match(prev, curr, max_dist=50):
    if not prev:
        return [], list(range(len(curr)))

    dist = np.zeros((len(prev), len(curr)))
    for i, p in enumerate(prev):
        for j, c in enumerate(curr):
            dist[i, j] = np.linalg.norm(np.array(p) - np.array(c))

    r, c = linear_sum_assignment(dist)

    matches = []
    new = []
    used = set()

    for i, j in zip(r, c):
        if dist[i, j] < max_dist:
            matches.append((i, j))
            used.add(j)

    for j in range(len(curr)):
        if j not in used:
            new.append(j)

    return matches, new

def track(images):
    tracks = {}
    prev = []
    ids = []
    next_id = 0

    for img in images:
        curr = get_centroids(img)

        if not prev:
            for c in curr:
                tracks[next_id] = [c]
                ids.append(next_id)
                next_id += 1
        else:
            matches, new = match(prev, curr)
            new_ids = [None] * len(curr)

            for i, j in matches:
                tid = ids[i]
                tracks[tid].append(curr[j])
                new_ids[j] = tid

            for j in new:
                tracks[next_id] = [curr[j]]
                new_ids[j] = next_id
                next_id += 1

            ids = new_ids

        prev = curr

    return tracks

def plot_tracks(tracks):
    plt.figure()

    for pts in tracks.values():
        pts = np.array(pts)
        plt.plot(pts[:,0], pts[:,1], '-o', color='blue')

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Object trajectories")
    plt.grid()
    plt.axis("equal")

    plt.savefig("trajectories.png", dpi=300)  # сохранение графика
    plt.show()

images = load_images("images")
tracks = track(images)
plot_tracks(tracks)