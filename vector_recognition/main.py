import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
from skimage.io import imread
from pathlib import Path

save_path = Path(__file__).parent

def load_binary(path, invert=False):
        img = imread(path)
        if img.ndim == 3:
            img = img[..., :3].mean(axis=2)
        return img < 128 if invert else img > 0

def count_holes(region):
        img = np.pad(region.image, 1)
        return label(~img).max() - 1

def extractor(region):
        img = region.image
        h, w = img.shape
        cy, cx = region.centroid_local

        return np.array([
            region.area / img.size,
            cy / h,
            cx / w,
            region.perimeter / region.area if region.area else 0, 
            count_holes(region),
            (img.sum(axis=1) == w).sum(),
            (img.sum(axis=0) == h).sum(),
            region.eccentricity,
            h / w
        ])

def classify(region, templates):
        f = extractor(region)
        return min(templates, key=lambda s: np.linalg.norm(templates[s] - f))


template_symbols = ["A","B","8","0","1","W","X","*","-","/"]

template_img = load_binary("alphabet.png")
template_regions = regionprops(label(template_img))

templates = {
        s: extractor(r)
        for s, r in zip(template_symbols, template_regions)
    }



img = load_binary("alphabet.png")
regions = regionprops(label(img))

results = {}

plt.switch_backend("Agg")

for r in regions:
        symbol = classify(r, templates)
        results[symbol] = results.get(symbol, 0) + 1

        plt.imshow(r.image, cmap="gray")
        plt.title(symbol)
        plt.axis("off")
        plt.savefig(save_path / f"image_{r.label}.png")
        plt.clf()


print("\nРезультаты:")
for s in sorted(results):
    print(f"{s}: {results[s]}")

total = len(regions)
unknown = results.get("?", 0)

print(f"\nВсего: {total}")
print(f"Точность: {(1 - unknown/total):.2%}")


plt.imshow(img, cmap="gray")
plt.axis("off")
plt.savefig(save_path / "overview.png")
plt.close()
