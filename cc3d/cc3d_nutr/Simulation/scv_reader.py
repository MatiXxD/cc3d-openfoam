import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import csv

def create_csv_for_CC3D():
    # размеры сетки
    NX = NY = NZ = 64

    # диапазон координат
    xmin = ymin = zmin = 0
    xmax = ymax = zmax = 63

    # генерируем координаты
    x = np.linspace(xmin, xmax, NX)
    y = np.linspace(ymin, ymax, NY)
    z = np.linspace(zmin, zmax, NZ)

    # центр сферы
    cx = cy = cz = 32

    # радиус
    R = 20

    # имя выходного CSV
    filename = "field.csv"

    with open(filename, mode="w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")

        # заголовок
        writer.writerow(['CON', "Points:0", "Points:1", "Points:2"])

        # тройной цикл по сетке
        for xi in x:
            for yi in y:
                for zi in z:

                    # расстояние до центра
                    r = np.sqrt((xi - cx)**2 + (yi - cy)**2 + (zi - cz)**2)

                    # значение C: внутри сферы — 11, снаружи — 0
                    C = 1.7 if r <= R else 0

                    writer.writerow([C, xi, yi, zi])

    print(f"Файл '{filename}' успешно создан.")

df = pd.read_csv("dumps/new_nutr_field.csv")
nutrField_csv = df['CON'].to_numpy()
print(nutrField_csv)
values = df["CON"].to_numpy().reshape((64, 64, 64))


cx = 31
cy = 31
cz = 31

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

im0 = axes[0].imshow(values[cx, :, :], origin='lower')
im1 = axes[1].imshow(values[:, cy, :], origin='lower')
im2 = axes[2].imshow(values[:, :, cz], origin='lower')

fig.colorbar(im0, ax=axes[0])
fig.colorbar(im1, ax=axes[1])
fig.colorbar(im2, ax=axes[2])


plt.tight_layout()

plt.savefig("asdf.pdf")
plt.close(fig)
