import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
import pyvista as pv
import matplotlib.pyplot as plt
import meshio
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
import math


import pandas as pd
from scipy.interpolate import RegularGridInterpolator


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
    # print("Создан файл:", out_filename)

    # values = df_new["CON"].to_numpy().reshape((64, 64, 64))
    #
    # cx = 31
    # cy = 31
    # cz = 31
    #
    # fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    #
    # axes[0].imshow(values[cx, :, :], origin='lower')
    # axes[0].set_title(f"{CON} — slice X={cx}")
    #
    # axes[1].imshow(values[:, cy, :], origin='lower')
    # axes[1].set_title(f"{CON} — slice Y={cy}")
    #
    # axes[2].imshow(values[:, :, cz], origin='lower')
    # axes[2].set_title(f"{CON} — slice Z={cz}")
    #
    # plt.tight_layout()
    # plt.show()



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
                s[-1] = 1
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
        matrix[id_x, id_y, id_z] = is_cell
    return matrix


def CC3D_to_OF_stl(time):
    file_path = "dumps/dump_cc3d.txt"  # замените на свой путь к файлу

    with open(file_path, 'r') as f:

        block_data, border_voxels, nxyz = read_block_lines(f)
        nx, ny, nz = nxyz[0], nxyz[1], nxyz[2]
        matrix = create_3dmatrix(block_data, nx, ny, nz)


        #with open("/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_integration/OpenFoamProject/constant/triSurface/sphere" + str(time) +".stl", "w") as mesh_stl:
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

vtk_to_stl("/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_nutr/OF_dumps/D_ts49/VTK/Diffusion_14.vtk", "dumps/new_nutr_field.csv")
#vtk_to_stl("/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_nutr/OF_dumps/D_ts50/VTK/Diffusion_14.vtk")

