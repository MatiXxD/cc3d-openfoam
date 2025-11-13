import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
import pyvista as pv
import matplotlib.pyplot as plt


def skip_first_steps(file, num_skip):
    for _ in range(num_skip):
        empty_line_count = 0
        for line in file:
            if line.strip() == '':
                empty_line_count += 1
                if empty_line_count == 2:
                    break

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





def plot_matrix(matrix, time):

    x, y, z = np.where(matrix == 1)

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c='red', marker='o')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 9)
    ax.set_zlim(0, 9)

    plt.title('Маска 3D матрицы: красные точки — единицы')
    plt.savefig("3dmap" + str(time) + ".png", dpi = 400)


def create_3dmatrix(data, nx, ny, nz):
    matrix = np.zeros((nx, ny, nz), dtype=int)
    for id_x, id_y, id_z, is_cell in data:
        matrix[id_x, id_y, id_z] = is_cell
    return matrix


def create_mesh_for_OF(time):
    file_path = "/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_integration/dumps/dump_cc3d.txt"  # замените на свой путь к файлу

    with open(file_path, 'r') as f:
        skip_first_steps(f, num_skip =0)  # 0, если сразу хотим читать первый блок
        block_data, border_voxels, nxyz = read_block_lines(f)
        nx, ny, nz = nxyz[0], nxyz[1], nxyz[2]
        matrix = create_3dmatrix(block_data, nx, ny, nz)


        #with open("/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_integration/OpenFoamProject/constant/triSurface/sphere" + str(time) +".stl", "w") as mesh_stl:
        with open("/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_integration/OpenFoamProject/constant/triSurface/sphere.stl", "w") as mesh_stl:
            mesh_stl.write("solid Visualization Toolkit generated SLA File\n")
            make_stl_file(mesh_stl, matrix, nx, ny, nz)
            mesh_stl.write("endsolid")



    # reader = pv.get_reader("/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_integration/OpenFoamProject/constant/triSurface/sphere.stl")
    # mesh = reader.read()
    #
    # print(mesh)
    # normals = mesh.cell_normals
    # centers = mesh.cell_centers().points



    # plotter = pv.Plotter()
    # plotter.add_mesh(mesh, color="lightblue", show_edges=True, opacity=1.0)
    # plotter.add_arrows(centers, normals, mag=0.2, color='red')
    # plotter.add_axes()
    # plotter.save_graphic("mesh_view" + str(time) + ".pdf")





