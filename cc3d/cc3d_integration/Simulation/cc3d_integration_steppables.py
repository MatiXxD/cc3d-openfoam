from cc3d.core.PySteppables import *
import numpy as np
import time
import subprocess



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
    cpp_source = "../cpp_example/main"          # путь к бинарю (для примера простой cpp код)
    dumpfile_cc3d = "../dumps/dump_cc3d.txt"    # куда будем писать границу из cc3d
    dumpfile_cpp = "../dumps/dump_cpp.txt"      # имя файла, куда будет записан результат обработки
    dump_time = 100

    def __init__(self,frequency=1):
        SteppableBasePy.__init__(self, frequency)

    def start(self):
        pass

    def step(self, mcs):
        if mcs % self.dump_time != 0:
            return

        # 1. получаем границу клеток + записываем в stl формат
        self._calc_boundary_stub()

        # 2. вызываем внешний процесс (openfoam) для обработки границы
        subprocess.run([self.cpp_source, self.dumpfile_cc3d, self.dumpfile_cpp])

        # 3. читаем результат из файла, который был запсан openfoam + обновляем клетки
        self._update_cells_stub()

    def _calc_boundary_stub(self):
        with open(self.dumpfile_cc3d, "w") as f:
            f.write("TESTING\n")
            f.write("1 2 3\n")

    def _update_cells_stub(self):
        with open(self.dumpfile_cpp, "r") as f:
            f.readline()
            data = f.readline().split()
            print("got processed data: ", data)