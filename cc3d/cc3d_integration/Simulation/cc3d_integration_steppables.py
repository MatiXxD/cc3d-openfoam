from cc3d.core.PySteppables import *
import numpy as np
import time
import subprocess
import cell_to_mech
from cell_to_mech import create_mesh_for_OF

class ConstraintInitializerSteppable(SteppableBasePy):
    def __init__(self,frequency=1):
        SteppableBasePy.__init__(self,frequency)

    def start(self):
        for cell in self.cell_list:
            cell.targetVolume = 25
            cell.lambdaVolume = 2.0


class GrowthSteppable(SteppableBasePy):
    def __init__(self,frequency=1):
        SteppableBasePy.__init__(self, frequency)
    def step(self, mcs):
        for cell in self.cell_list:
            cell.targetVolume += 1


class PixelTrackerSteppable(SteppableBasePy):
    cpp_source = "../cpp_example/main.cpp"          # путь к бинарю (для примера простой cpp код)
    dumpfile_cc3d = "/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_integration/dumps/dump_cc3d.txt"    # куда будем писать границу из cc3d
    dumpfile_cpp = "/home/softmatter/Documents/CC3D-OF/MAIN/cc3d/cc3d_integration/dumps/dump_cpp.txt"      # имя файла, куда будет записан результат обработки
    dump_time = 100

    def __init__(self,frequency=1):
        SteppableBasePy.__init__(self, frequency)

    def start(self):
        pass

    def step(self, mcs):
        if mcs % self.dump_time != 0:
            return

        # 1. получаем границу клеток + записываем в stl формат
        self._calc_boundary_stub(mcs)

        # 2. вызываем внешний процесс (openfoam) для обработки границы
        # subprocess.run([self.cpp_source, self.dumpfile_cc3d, self.dumpfile_cpp])
        # self.run_openFoam()

        # 3. читаем результат из файла, который был запсан openfoam + обновляем клетки
        self._update_cells_stub()

    def _calc_boundary_stub(self, mcs):
        with open(self.dumpfile_cc3d, "w") as f:
            f.write(f"TIMESTEP: {100}\n")
            f.write(f"FORMAT: x y z type\n")
            for x in range(self.dim.x):
                for y in range(self.dim.y):
                    for z in range(self.dim.z):
                        cell_type = 0
                        cell = self.cell_field[x, y, z]
                        if cell:
                            cell_type = cell.type
                        f.write(f"{x} {y} {z} {cell_type}\n")
            f.write(f"\n\n\n\n\n")
        create_mesh_for_OF(mcs)

    def run_openFoam(self):
        return


    def _update_cells_stub(self):
        with open(self.dumpfile_cpp, "r") as f:
            f.readline()
            data = f.readline().split()
            print("got processed data: ", data)
