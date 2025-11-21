#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ФИНАЛЬНАЯ ИСПРАВЛЕННАЯ версия: преобразование field данных в OpenFОАМ 0/T 
Использует Cx, Cy, Cz файлы (центры ячеек от OpenFOAM)

ФАЙЛ СОЗДАЕТСЯ ПРОСТО КАК T (БЕЗ ПАПКИ 0/)


Использование: python convert_field_to_T.py
Требует: pip install numpy scipy
"""

import sys
import os
import numpy as np

def read_field_file(filename):
    """Читает field.csv в формате: VALUE X Y Z (TAB-separated)
    Пропускает заголовок CON Points:0 Points:1 Points:2
    """
    data = []
    try:
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                if i == 0:  # пропускаем заголовок
                    print(f"Заголовок: {line.strip()}")
                    continue
                line_strip = line.strip()
                if not line_strip:
                    continue
                if filename =="dumps/nutr_field.csv":
                    parts = line_strip.split('\t')  # TAB-разделитель!
                else:
                    parts = line_strip.split(',')  # TAB-разделитель!
                if len(parts) >= 4:
                    try:
                        # ПРАВИЛЬНЫЙ порядок: VALUE X Y Z
                        value = float(parts[0])  # первая колонка - VALUE (концентрация)
                        x = float(parts[1])      # вторая - X координата
                        y = float(parts[2])      # третья - Y координата
                        z = float(parts[3])      # четвёртая - Z координата
                        data.append({'x': x, 'y': y, 'z': z, 'value': value})
                    except (ValueError, IndexError) as e:
                        continue
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден в текущей папке!")
        print(f"Текущая папка: {os.getcwd()}")
        print(f"Файлы в папке: {os.listdir('.')}")
        sys.exit(1)
    return data

def read_openfoam_component(filename):
    """Читает компоненту центров ячеек (Cx, Cy или Cz)"""
    values = []
    try:
        with open(filename, 'r') as f:
            reading = False
            for line in f:
                line_strip = line.strip()
                if line_strip == '(':
                    reading = True
                    continue
                elif line_strip == ')':
                    break
                if reading and line_strip:
                    try:
                        val = float(line_strip)
                        values.append(val)
                    except ValueError:
                        continue
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден в текущей папке!")
        print(f"Текущая папка: {os.getcwd()}")
        print(f"Файлы в папке: {os.listdir('.')}")
        sys.exit(1)
    return np.array(values)

def read_cell_centers(cx_file="Cx", cy_file="Cy", cz_file="Cz"):
    """Читает Cx, Cy, Cz и объединяет в координаты центров ячеек"""
    print(f"Чтение центров ячеек из: {cx_file}, {cy_file}, {cz_file}")
    
    cx = read_openfoam_component(cx_file)
    cy = read_openfoam_component(cy_file)
    cz = read_openfoam_component(cz_file)
    
    print(f"✓ Прочитано {len(cx)} значений x")
    print(f"✓ Прочитано {len(cy)} значений y")
    print(f"✓ Прочитано {len(cz)} значений z")
    
    if not (len(cx) == len(cy) == len(cz)):
        print(f"Ошибка: Разное количество координат!")
        print(f"  Cx: {len(cx)}, Cy: {len(cy)}, Cz: {len(cz)}")
        sys.exit(1)
    
    centers = []
    for i in range(len(cx)):
        centers.append({'x': cx[i], 'y': cy[i], 'z': cz[i]})
    
    print(f"✓ Объединено {len(centers)} центров ячеек")
    return centers

def match_values_to_mesh_kdtree(field_data, mesh_data):
    """Сопоставляет значения используя KD-дерево"""
    try:
        from scipy.spatial import cKDTree
    except ImportError:
        print("ОШИБКА: Требуется scipy")
        print("Установите: pip install scipy")
        sys.exit(1)
    
    if len(field_data) == 0:
        print("Ошибка: Нет данных в файле концентраций!")
        sys.exit(1)
    
    if len(mesh_data) == 0:
        print("Ошибка: Нет центров ячеек!")
        sys.exit(1)
    
    print(f"Точек в field: {len(field_data)}")
    print(f"Ячеек в mesh: {len(mesh_data)}")
    
    field_coords = np.array([[p['x'], p['y'], p['z']] for p in field_data])
    field_values = np.array([p['value'] for p in field_data])
    mesh_coords = np.array([[p['x'], p['y'], p['z']] for p in mesh_data])
    
    print(f"\nДиапазон field:  x=[{field_coords[:, 0].min():.2f}, {field_coords[:, 0].max():.2f}]")
    print(f"                 y=[{field_coords[:, 1].min():.2f}, {field_coords[:, 1].max():.2f}]")
    print(f"                 z=[{field_coords[:, 2].min():.2f}, {field_coords[:, 2].max():.2f}]")
    print(f"Диапазон mesh:   x=[{mesh_coords[:, 0].min():.2f}, {mesh_coords[:, 0].max():.2f}]")
    print(f"                 y=[{mesh_coords[:, 1].min():.2f}, {mesh_coords[:, 1].max():.2f}]")
    print(f"                 z=[{mesh_coords[:, 2].min():.2f}, {mesh_coords[:, 2].max():.2f}]")
    
    print(f"\nДиапазон значений: [{field_values.min():.4f}, {field_values.max():.4f}]")
    
    print("\nПостроение KD-дерева...")
    tree = cKDTree(field_coords)
    
    print("Поиск ближайших точек...")
    distances, indices = tree.query(mesh_coords, k=1)
    
    matched_values = field_values[indices]
    
    print(f"\n✓ Среднее расстояние: {distances.mean():.6f}")
    print(f"✓ Минимальное расстояние: {distances.min():.6f}")
    print(f"✓ Максимальное расстояние: {distances.max():.6f}")
    print(f"✓ Диапазон сопоставленных значений: [{matched_values.min():.4f}, {matched_values.max():.4f}]")
    
    max_distance = 10.0
    far_points = np.where(distances > max_distance)[0]
    if len(far_points) > 0:
        print(f"Предупреждение: {len(far_points)} ячеек на расстоянии > {max_distance}")
        matched_values[far_points] = 0.0
    
    return matched_values

def create_openfoam_T_file(values, output_file="T"):
    if os.path.exists(output_file):
        os.remove(output_file)
    """Создает файл T в текущей папке (БЕЗ папки 0/)"""
    N = len(values)
    
    if N == 0:
        print("Ошибка: Нет значений!")
        sys.exit(1)
    
    print(f"\nСоздание файла {output_file} с {N} значениями...")
    
    with open(output_file, 'w') as f:
        f.write("/*--------------------------------*- C++ -*----------------------------------*\\\n")
        f.write("  =========                 |\n")
        f.write("  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox\n")
        f.write("   \\    /   O peration     | Website:  https://openfoam.org\n")
        f.write("    \\  /    A nd           | Version:  10\n")
        f.write("     \\/     M anipulation  |\n")
        f.write("\\*---------------------------------------------------------------------------*/\n")
        f.write("FoamFile\n")
        f.write("{\n")
        f.write("    format      ascii;\n")
        f.write("    class       volScalarField;\n")
        f.write("    location    \"0\";\n")
        f.write("    object      T;\n")
        f.write("}\n")
        f.write("// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n")
        f.write("dimensions      [0 -3 0 0 1 0 0];\n\n")
        
        # ПРАВИЛЬНЫЙ ФОРМАТ
        f.write(f"internalField   nonuniform List<scalar> \n{N}\n(\n")
        
        for val in values:
            f.write(f"{val}\n")
        
        f.write(");\n\n")
        f.write("boundaryField\n")
        f.write("{\n")
        f.write("    inlet\n")
        f.write("    {\n")
        f.write("        type            fixedValue;\n")
        f.write("        value           uniform 0;\n")
        f.write("    }\n")
        f.write("    outlet\n")
        f.write("    {\n")
        f.write("        type            zeroGradient;\n")
        f.write("    }\n")
        f.write("    sides\n")
        f.write("    {\n")
        f.write("        type            zeroGradient;\n")
        f.write("    }\n")
        f.write("    sphere\n")
        f.write("    {\n")
        f.write("        type            fixedValue;\n")
        f.write("        value           uniform 0;\n")
        f.write("    }\n")
        f.write("}\n\n")
        f.write("// ************************************************************************* //\n")
    
    print(f"✓ Файл '{output_file}' успешно создан с {N} значениями.")

def make_T_file_for_OFD(msc, dump):
    if msc == dump -1:
        field_data = read_field_file("dumps/nutr_field.csv")
        mesh_data = read_cell_centers("/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_nutr/OpenFoamProject/BuilderForDiffusion/2/Cx",
        "/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_nutr/OpenFoamProject/BuilderForDiffusion/2/Cy",
        "/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_nutr/OpenFoamProject/BuilderForDiffusion/2/Cz")
        values = match_values_to_mesh_kdtree(field_data, mesh_data)
        create_openfoam_T_file(values, "T")
    else:
        print("new_nutr_field")
        field_data = read_field_file("dumps/new_nutr_field.csv")
        mesh_data = read_cell_centers("/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_nutr/OpenFoamProject/BuilderForDiffusion/2/Cx",
        "/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_nutr/OpenFoamProject/BuilderForDiffusion/2/Cy",
        "/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_nutr/OpenFoamProject/BuilderForDiffusion/2/Cz")
        values = match_values_to_mesh_kdtree(field_data, mesh_data)
        create_openfoam_T_file(values, "T")

make_T_file_for_OFD(99, 50)
