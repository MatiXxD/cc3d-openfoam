import numpy as np
import matplotlib as mpl
import sys
import meshio
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
import math
import os
import matplotlib.pyplot as plt



def upscale_stl_to_64(filename, out_filename):

    # === 1. Загружаем данные ===
    min_val=18
    max_val=81
    new_n=64

    df = pd.read_csv(filename)

    CON = df["CON"].to_numpy()
    X = df["Points:0"].to_numpy()
    Y = df["Points:1"].to_numpy()
    Z = df["Points:2"].to_numpy()
    U0 = df["U:0"].to_numpy()
    U1 = df["U:1"].to_numpy()
    U2 = df["U:2"].to_numpy()

    # === 2. Определяем размер старой сетки ===
    # Сетка 50×50×50
    N = int(round(len(CON) ** (1/3)))
    assert N**3 == len(CON), "Сетка не кубическая!"

    # === 3. Формируем координаты старой сетки ===
    xs = np.unique(X)      # [0,2,4,...,98]
    ys = np.unique(Y)
    zs = np.unique(Z)

    # reshape данных в 3D
    CON3 = CON.reshape((N, N, N))
    U0_3 = U0.reshape((N, N, N))
    U1_3 = U1.reshape((N, N, N))
    U2_3 = U2.reshape((N, N, N))

    # === 4. Создаём новую 64×64×64 сетку ===
    new_x = np.linspace(min_val, max_val, new_n)
    new_y = np.linspace(min_val, max_val, new_n)
    new_z = np.linspace(min_val, max_val, new_n)

    Xn, Yn, Zn = np.meshgrid(new_x, new_y, new_z, indexing='ij')

    points_new = np.vstack([Xn.ravel(), Yn.ravel(), Zn.ravel()]).T

    # === 5. Интерполяторы ===
    interp_CON = RegularGridInterpolator((xs, ys, zs), CON3)
    interp_U0  = RegularGridInterpolator((xs, ys, zs), U0_3)
    interp_U1  = RegularGridInterpolator((xs, ys, zs), U1_3)
    interp_U2  = RegularGridInterpolator((xs, ys, zs), U2_3)

    # === 6. Интерполяция ===
    new_CON = interp_CON(points_new)
    new_U0  = interp_U0(points_new)
    new_U1  = interp_U1(points_new)
    new_U2  = interp_U2(points_new)

    # === 7. Готовим DataFrame ===
    df_new = pd.DataFrame({
        "CON": new_CON,
        "Points:0": points_new[:, 0]-min_val,
        "Points:1": points_new[:, 1]-min_val,
        "Points:2": points_new[:, 2]-min_val,
        "U:0": new_U0,
        "U:1": new_U1,
        "U:2": new_U2
    })

    # === 8. Сохраняем ===
    df_new.to_csv(out_filename, index=False, float_format="%.6g")


def vtk_to_stl(vtk_name, stl_name):
    mesh = meshio.read(vtk_name)
    points = mesh.points
    point_data = mesh.point_data

    # Используем поля из point_data
    T = point_data.get('T')
    U = point_data.get('U')

    if T is None or U is None:
        raise ValueError("Отсутствует поле T или U в point_data")

    df = pd.DataFrame({
        'CON': T,
        'Points:0': points[:, 0] + abs(min(points[:, 0])),
        'Points:1': points[:, 1] + abs(min(points[:, 1])),
        'Points:2': points[:, 2] + abs(min(points[:, 2])),
        'U:0': U[:, 0],
        'U:1': U[:, 1],
        'U:2': U[:, 2],
    })

    df.to_csv(stl_name, index=False, float_format='%.6g')
    upscale_stl_to_64(stl_name, stl_name)






def read_block_lines(file):
    nx = -100
    ny = -100
    nz = -100
    data = []
    border_voxels = []

    empty_line_count = 0
    counter = 0
    for line in file:
        counter += 1
        if line.strip() == '':
            empty_line_count += 1
            if empty_line_count == 2:
                break
        elif counter > 2:
            empty_line_count = 0
            s = [int(float(item)) for item in line.strip().split()]

            if s[0] > nx:
                nx = s[0]
            if s[1] >ny:
                ny = s[1]
            if s[2] > nz:
                nz = s[2]

            data.append(s)
            if(s[-1] > 0.5):
                #s[-1] = 1
                border_voxels.append(s)
    return np.array(data), np.array(border_voxels), np.array([nx+1, ny+1, nz+1])






def write_left_triangles(f, arr, i, j, k):
    f.write(" facet normal " + str(float(1)) + " "+ str(float(0)) + " "+ str(float(0)) + "\n")
    f.write("  outer loop\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j)) + " " + str(float(k)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j)) + " " + str(float(k+1)) + "\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j)) + " " + str(float(k+1)) + "\n")
    f.write("  endloop\n")
    f.write(" endfacet\n")

    f.write(" facet normal " + str(float(0)) + " "+ str(float(1)) + " "+ str(float(0)) + "\n")
    f.write("  outer loop\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j)) + " " + str(float(k)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j)) + " " + str(float(k+1)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j)) + " " + str(float(k)) + "\n")
    f.write("  endloop\n")
    f.write(" endfacet\n")

def write_right_triangles(f, arr, i, j, k):
    f.write(" facet normal " + str(float(0)) + " "+ str(float(-1)) + " "+ str(float(0)) + "\n")
    f.write("  outer loop\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j+1)) + " " + str(float(k)) + "\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j+1)) + " " + str(float(k+1)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j+1)) + " " + str(float(k)) + "\n")
    f.write("  endloop\n")
    f.write(" endfacet\n")

    f.write(" facet normal " + str(float(0)) + " "+ str(float(-1)) + " "+ str(float(0)) + "\n")
    f.write("  outer loop\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j+1)) + " " + str(float(k+1)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j+1)) + " " + str(float(k+1)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j+1)) + " " + str(float(k)) + "\n")
    f.write("  endloop\n")
    f.write(" endfacet\n")

def write_upper_triangles(f, arr, i, j, k):

    f.write(" facet normal " + str(float(0)) + " "+ str(float(0)) + " "+ str(float(1)) + "\n")
    f.write("  outer loop\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j)) + " " + str(float(k+1)) + "\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j+1)) + " " + str(float(k+1)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j)) + " " + str(float(k+1)) + "\n")
    f.write("  endloop\n")
    f.write(" endfacet\n")

    f.write(" facet normal " + str(float(0)) + " "+ str(float(0)) + " "+ str(float(1)) + "\n")
    f.write("  outer loop\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j+1)) + " " + str(float(k+1)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j+1)) + " " + str(float(k+1)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j)) + " " + str(float(k+1)) + "\n")
    f.write("  endloop\n")
    f.write(" endfacet\n")



def write_lower_triangles(f, arr, i, j, k):

    f.write(" facet normal " + str(float(0)) + " "+ str(float(0)) + " "+ str(float(-1)) + "\n")
    f.write("  outer loop\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j)) + " " + str(float(k)) + "\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j+1)) + " " + str(float(k)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j)) + " " + str(float(k)) + "\n")
    f.write("  endloop\n")
    f.write(" endfacet\n")

    f.write(" facet normal " + str(float(0)) + " "+ str(float(0)) + " "+ str(float(-1)) + "\n")
    f.write("  outer loop\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j+1)) + " " + str(float(k)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j+1)) + " " + str(float(k)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j)) + " " + str(float(k)) + "\n")
    f.write("  endloop\n")
    f.write(" endfacet\n")

def write_forward_triangles(f, arr, i, j, k):

    f.write(" facet normal " + str(float(1)) + " "+ str(float(0)) + " "+ str(float(0)) + "\n")
    f.write("  outer loop\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j)) + " " + str(float(k)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j+1)) + " " + str(float(k)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j)) + " " + str(float(k+1)) + "\n")
    f.write("  endloop\n")
    f.write(" endfacet\n")

    f.write(" facet normal " + str(float(1)) + " "+ str(float(0)) + " "+ str(float(0)) + "\n")
    f.write("  outer loop\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j)) + " " + str(float(k+1)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j+1)) + " " + str(float(k+1)) + "\n")
    f.write("   vertex " + str(float(i+1)) + " " + str(float(j+1)) + " " + str(float(k)) + "\n")
    f.write("  endloop\n")
    f.write(" endfacet\n")


def write_backward_triangles(f, arr, i, j, k):

    f.write(" facet normal " + str(float(-1)) + " "+ str(float(0)) + " "+ str(float(0)) + "\n")
    f.write("  outer loop\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j)) + " " + str(float(k)) + "\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j)) + " " + str(float(k+1)) + "\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j+1)) + " " + str(float(k+1)) + "\n")
    f.write("  endloop\n")
    f.write(" endfacet\n")

    f.write(" facet normal " + str(float(-1)) + " "+ str(float(0)) + " "+ str(float(0)) + "\n")
    f.write("  outer loop\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j)) + " " + str(float(k)) + "\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j+1)) + " " + str(float(k)) + "\n")
    f.write("   vertex " + str(float(i)) + " " + str(float(j+1)) + " " + str(float(k+1)) + "\n")
    f.write("  endloop\n")
    f.write(" endfacet\n")


def make_stl_file(f, arr, nx, ny, nz):
    for k in range(1, nz-1):
        for j in range(1,  ny-1):
            for i in range(1, nx-1):
                if arr[i, j, k] > 0.5:

                    if arr[i, j-1, k] < 0.5:
                        write_left_triangles(f, arr, i, j, k)
                    if not arr[i, j+1, k]:
                        write_right_triangles(f, arr, i, j, k)

                    if not arr[i, j, k + 1]:
                        write_upper_triangles(f, arr, i, j, k)
                    #
                    if not arr[i, j, k-1]:
                        write_lower_triangles(f, arr, i, j, k)

                    if not arr[i+1, j, k]:
                        write_forward_triangles(f, arr, i, j, k)

                    if not arr[i-1, j, k]:
                        write_backward_triangles(f, arr, i, j, k)



def create_3dmatrix(data, nx, ny, nz):
    matrix = np.zeros((nx, ny, nz), dtype=int)
    for id_x, id_y, id_z, is_cell in data:

        matrix[id_x, id_y, id_z] = int(is_cell)
    return matrix









def read_field_file(filename):
    # Пропускает заголовок CON Points:0 Points:1 Points:2

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

def make_T_file_for_OFD(msc, field_path, OFD_case_dir_build, dump):
    if msc == dump -1:
        field_data = read_field_file(field_path + "/nutr_field.csv")
        mesh_data = read_cell_centers(
        OFD_case_dir_build+"/2/Cx",
        OFD_case_dir_build+"/2/Cy",
        OFD_case_dir_build+"/2/Cz")
        values = match_values_to_mesh_kdtree(field_data, mesh_data)
        create_openfoam_T_file(values, "T")
    else:
        field_data = read_field_file(field_path + "/new_nutr_field.csv")
        mesh_data = read_cell_centers(
        OFD_case_dir_build+"/2/Cx",
        OFD_case_dir_build+"/2/Cy",
        OFD_case_dir_build+"/2/Cz")
        values = match_values_to_mesh_kdtree(field_data, mesh_data)
        create_openfoam_T_file(values, "T")










def CC3D_to_OF_stl(time, flag):
    file_path = "dumps/dump_cc3d.txt"  # замените на свой путь к файлу

    with open(file_path, 'r') as f:

        block_data, border_voxels, nxyz = read_block_lines(f)
        nx, ny, nz = nxyz[0], nxyz[1], nxyz[2]
        matrix = create_3dmatrix(block_data, nx, ny, nz)

        with open("../OpenFoamProject/Hydrodynamic/constant/triSurface/sphere.stl", "w") as mesh_stl:
            mesh_stl.write("solid Visualization Toolkit generated SLA File\n")
            make_stl_file(mesh_stl, matrix, nx, ny, nz)
            mesh_stl.write("endsolid")

        with open("../OpenFoamProject/Diffusion/constant/triSurface/sphere.stl", "w") as mesh_stl:
            mesh_stl.write("solid Visualization Toolkit generated SLA File\n")
            make_stl_file(mesh_stl, matrix, nx, ny, nz)
            mesh_stl.write("endsolid")

        with open("../OpenFoamProject/BuilderForDiffusion/constant/triSurface/sphere.stl", "w") as mesh_stl:
            mesh_stl.write("solid Visualization Toolkit generated SLA File\n")
            make_stl_file(mesh_stl, matrix, nx, ny, nz)
            mesh_stl.write("endsolid")
        if(flag):

            cx = 31
            cy = 31
            cz = 31
            #print(*matrix[cx, :, :], sep = "\n")
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            im0 = axes[0].imshow(matrix[cx, :, :], origin='lower')
            im1 = axes[1].imshow(matrix[:, cy, :], origin='lower')
            im2 = axes[2].imshow(matrix[:, :, cz], origin='lower')
            axes[0].set_title("YZ")
            axes[1].set_title("XZ")
            axes[2].set_title("XY")
            fig.colorbar(im0, ax=axes[0])
            fig.colorbar(im1, ax=axes[1])
            fig.colorbar(im2, ax=axes[2])
            plt.tight_layout()
            plt.savefig("Ris/Cell" + str(time) +".pdf")
            plt.close(fig)

#vtk_to_stl("/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_nutr/OF_dumps/D_ts49/VTK/Diffusion_14.vtk", "dumps/new_nutr_field.csv")
#vtk_to_stl("/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_nutr/OF_dumps/D_ts50/VTK/Diffusion_14.vtk")

