import pandas as pd

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

create_csv_for_CC3D()
