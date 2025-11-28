from cc3d.cpp import CompuCell
from cc3d.core.PySteppables import *
import numpy as np
import subprocess

#import convert_field_to_T_final
#from convert_field_to_T_final import make_T_file_for_OFD
import formatters
from formatters import CC3D_to_OF_stl
from formatters import vtk_to_stl
from formatters import make_T_file_for_OFD

import pandas as pd

import openFoam_commands
from openFoam_commands import plot_nutr_field
from openFoam_commands import copy_last_OF_tms
from openFoam_commands import clear_OF_project
from openFoam_commands import write_boundary_for_OFD
from openFoam_commands import rename_last_tms
from openFoam_commands import return_initial_zero_folder
from openFoam_commands import copy_vtk_folder

import convert_field_to_S_final
from convert_field_to_S_final import make_S_file_for_OFD

class ConstraintInitializerSteppable(SteppableBasePy):
    def __init__(self, frequency=1, params={}):
        SteppableBasePy.__init__(self, frequency)
        self.TARGET_VOLUME = params["targetVolume"]
        self.LAMBDA_VOLUME = params["lambdaVolume"]
        self.RATIO = params["ratio"]
        self.TARGET_SURFACE = self.RATIO * (
            4 * np.pi * (3 * self.TARGET_VOLUME / (4.0 * np.pi)) ** (2.0 / 3.0)
        )
        self.LAMBDA_SURFACE = params["lambdaSurface"]
        self.TIME_TO_DEATH = params["timeToDeath"]

    def start(self):
        for cell in self.cell_list:
            cell.targetVolume = self.TARGET_VOLUME
            cell.lambdaVolume = self.LAMBDA_VOLUME
            cell.targetSurface = self.TARGET_SURFACE
            cell.lambdaSurface = self.LAMBDA_SURFACE
            cell.dict["time_to_death"] = self.TIME_TO_DEATH


class GrowthSteppable(SteppableBasePy):

    def __init__(self, frequency=1, sim_name="default", params={}):
        SteppableBasePy.__init__(self, frequency)
        self.filename = sim_name
        self.init_files()

        self.RATIO = params["ratio"]
        self.CONCENTRATION_MIN = params["concentraion_min"]
        self.CONCENTRATION_MAX = params["concentraion_max"]
        self.CELL_UPTAKE = params["cellUptake"]
        self.CELL_UPTAKE_RELATIVE = params["cellUptakeRelative"]
        self.DELTA_DEATH = params["deltaDeath"]
        self.DELTA_VOLUME = params["deltaVolume"]
        self.CRIT_VOLUME = params["critVolume"]
        self.DUMP_TIME = params["dump_time"]
        self.TIME_TO_DEATH = params["timeToDeath"]



        self.dumpfile_cc3d = "dumps/dump_cc3d.txt"    # куда будем писать границу из cc3d
        self.dumpfile_secretion = "dumps/dump_secretion.txt"    # куда будем писать границу из cc3d
        self.dumpfile_nutr = "dumps/dump_nutr.txt"    # куда будем писать концентрацию нутр
        self.dumpfile_csv = "field_cc3d.csv"      # имя файла, куда будет записан результат обработки
        self.OFH_case_dir = "../OpenFoamProject/Hydrodynamic"
        self.OFD_case_dir = "../OpenFoamProject/Diffusion"
        self.OFD_case_dir_build = "../OpenFoamProject/BuilderForDiffusion"
        self.OFH_dump_dir = "../OF_dumps/H_ts"
        self.OFD_dump_dir = "../OF_dumps/D_ts"





    def get_surface(self, vol):
        return self.RATIO * (4 * np.pi * (3 * vol / (4.0 * np.pi)) ** (2.0 / 3.0))

    def init_files(self):
        self.filename += ".dat"
        with open(self.filename, "w") as f:
            pass

    # создает дамп файл клеточного сгустка
    def create_cc3d_dump(self, mcs):
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

    # создает дамп файл секреции (поглщения) питательных веществ
    def create_secretion_dump(self, mcs):
        with open(self.dumpfile_secretion, "w") as f:
            f.write(f"TIMESTEP: {100}\n")
            f.write(f"FORMAT: x y z Q\n")
            for x in range(self.dim.x):
                for y in range(self.dim.y):
                    for z in range(self.dim.z):
                        cell_type = 0
                        cell = self.cell_field[x, y, z]
                        uptake = 0
                        if cell:
                            cell_type = cell.type
                            if(cell_type != 3):
                                uptake = self.CELL_UPTAKE
                        f.write(f"{x} {y} {z} {uptake}\n")
            f.write(f"\n\n\n\n\n")


    # создает файл концентрации питательных веществ
    def create_nutr_dump(self, mcs, nutrField):
        with open(self.dumpfile_nutr, "w") as f:
            f.write(f"TIMESTEP: {100}\n")
            f.write(f"FORMAT: x y z C_nutr\n")
            for xc in range(self.dim.x):
                for yc in range(self.dim.y):
                    for zc in range(self.dim.z):
                        nutrValue = nutrField[xc, yc, zc]
                        f.write(f"{xc} {yc} {zc} {nutrValue}\n")
            f.write(f"\n\n\n\n\n")

    # импорт новго файла питательных вещетсво после расчета опенфома
    def set_custome_nutr(self, nutrField, mcs):
        if mcs == 0:
            df = pd.read_csv("dumps/nutr_field.csv", sep="\t")
            nutrField_csv = df['CON'].to_numpy()
            for x in range(self.dim.x):
                for y in range(self.dim.y):
                    for z in range(self.dim.z):
                        # i=x⋅(NY⋅NZ)+y⋅NZ+z
                        nutrField[x, y, z] = float(nutrField_csv[x *self.dim.y * self.dim.z + y * self.dim.z + z])
            plot_nutr_field(df, mcs)
        else:
            df = pd.read_csv("dumps/new_nutr_field.csv")
            nutrField_csv = df['CON'].to_numpy()
            for x in range(self.dim.x):
                for y in range(self.dim.y):
                    for z in range(self.dim.z):
                        # i=x⋅(NY⋅NZ)+y⋅NZ+z
                        nutrField[x, y, z] = float(nutrField_csv[x *self.dim.y * self.dim.z + y * self.dim.z + z])
            plot_nutr_field(df, mcs)

    # заапуск гидроднамики
    def run_OFH_command(self, mcs):
        ##rabotaet no nado ustanovit openfoam.
        return_initial_zero_folder(self.OFH_case_dir, "../OpenFoamProject/0_Hydro")
        subprocess.run(["blockMesh", "-case", self.OFH_case_dir], check=True)
        subprocess.run(["snappyHexMesh", "-overwrite", "-case", self.OFH_case_dir], check=True)
        subprocess.run(["icoFoam", "-case", self.OFH_case_dir], check=True)




    # подготовительный проект дифузии
    def build_OFD_project(self, mcs, dump):

        subprocess.run(["blockMesh", "-case", self.OFD_case_dir_build], check=True)
        write_boundary_for_OFD("../OpenFoamProject/D_boundary", self.OFD_case_dir_build + "/constant/polyMesh/boundary")
        rename_last_tms(self.OFH_case_dir)
        subprocess.run(["mapFields", "-case", self.OFD_case_dir_build, self.OFH_case_dir, "-consistent"], check=True)
        subprocess.run(["topoSet", "-case", self.OFD_case_dir_build], check=True)
        subprocess.run(["scalarTransportFoam", "-case", self.OFD_case_dir_build], check=True)
        subprocess.run(["postProcess", "-func", "writeCellCentres", "-latestTime", "-case", self.OFD_case_dir_build], check=True)
        make_T_file_for_OFD(mcs, "dumps", self.OFD_case_dir_build, dump)
        write_boundary_for_OFD("T", self.OFD_case_dir + "/0/T")
        make_S_file_for_OFD(mcs, "dumps", self.OFD_case_dir_build, dump)
        write_boundary_for_OFD("S", self.OFD_case_dir + "/0/S")




    # запуск проекта диффузии через опенфом
    def run_OFD_command(self, mcs):
        subprocess.run(["blockMesh", "-case", self.OFD_case_dir], check=True)
        write_boundary_for_OFD("../OpenFoamProject/D_boundary", self.OFD_case_dir + "/constant/polyMesh/boundary")
        subprocess.run(["mapFields", "-case", self.OFD_case_dir, self.OFH_case_dir, "-consistent"], check=True)
        subprocess.run(["topoSet", "-case", self.OFD_case_dir], check=True)
        subprocess.run(["scalarTransportFoam", "-case", self.OFD_case_dir], check=True)
        copy_last_OF_tms(mcs, self.OFD_case_dir, self.OFD_dump_dir)
        #make vtk of lst tmst
        subprocess.run(["foamToVTK", "-case", self.OFD_case_dir, "-ascii", "-latestTime"], check=True)
        copy_vtk_folder(mcs, self.OFD_case_dir, self.OFD_dump_dir)
        ## new nutr_field in stl format
        vtk_to_stl(self.OFD_dump_dir + str(mcs) + "/VTK/Diffusion_14.vtk",        "dumps/new_nutr_field.csv")

    def step(self, mcs):

        secretor = self.get_field_secretor("nutr")
        nutrField = self.field.nutr

        # ===============================================================================
        # download the nutrient field from OF || download the nutrient field from OF
        # ===============================================================================
        if mcs % self.DUMP_TIME == 0:
            self.set_custome_nutr(nutrField, mcs)
            print("STEP:", mcs)


        for cell in self.cell_list:
            if cell.type in [self.CELL, self.CELLGROW, self.CELLHYPO]:
                secretor.uptakeInsideCell(
                    cell, self.CELL_UPTAKE, self.CELL_UPTAKE_RELATIVE
                )
                xc, yc, zc = cell.xCOM, cell.yCOM, cell.zCOM
                nutrValue = nutrField[xc, yc, zc]


                if cell.type == self.CELL:
                    if nutrValue >= self.CONCENTRATION_MAX:
                        cell.type = self.CELLGROW
                    elif nutrValue <= self.CONCENTRATION_MIN:
                        cell.type = self.CELLHYPO

                elif cell.type == self.CELLHYPO:
                    if nutrValue > self.CONCENTRATION_MIN:
                        cell.type = self.CELL
                        cell.dict["time_to_death"] = self.TIME_TO_DEATH
                    elif cell.dict["time_to_death"] > 0:
                        cell.dict["time_to_death"] -= 1
                    elif cell.dict["time_to_death"] <= 0:
                        cell.type = self.CELLDEAD

                elif cell.type == self.CELLGROW:
                    if nutrValue < self.CONCENTRATION_MAX:
                        cell.type = self.CELL
                    else:
                        cell.targetVolume += self.DELTA_VOLUME
                        cell.targetSurface = self.get_surface(cell.targetVolume)

            elif cell.type == self.CELLDEAD and cell.targetVolume > 0:
                if cell.targetVolume <= 5:
                    cell.targetVolume = 0
                    cell.lambdaVolume = 1000
                    cell.targetSurface = 0
                    cell.lambdaSurface = 1000
                else:
                    cell.targetVolume -= self.DELTA_DEATH
                    cell.targetSurface = self.get_surface(cell.targetVolume)


        # ===============================================================================
        # OpenFoamPart---OpenFoamPart---OpenFoamPart---OpenFoamPart---OpenFoamPart---
        # ===============================================================================
        if mcs > 0 and mcs % self.DUMP_TIME == self.DUMP_TIME-1:
            # создание и конвертация данных для опенфома
            self.create_cc3d_dump(mcs)
            self.create_secretion_dump(mcs)
            CC3D_to_OF_stl(mcs, 1)
            self.create_nutr_dump(mcs, nutrField)

            # запуск гидродинамики и сохранение результата
            self.run_OFH_command(mcs)

            copy_last_OF_tms(mcs, self.OFH_case_dir, self.OFH_dump_dir)

            # Запус проектов по диффузии - подготовка и общий
            self.build_OFD_project(mcs, self.DUMP_TIME)
            self.run_OFD_command(mcs)

        if mcs > 0 and mcs % self.DUMP_TIME == 1:
            # очистка директорий проектов опен фома
            clear_OF_project(mcs, self.OFD_case_dir, self.OFD_dump_dir)
            clear_OF_project(mcs, self.OFH_case_dir, self.OFH_dump_dir)





class MitosisSteppable(MitosisSteppableBase):
    def __init__(self, frequency=1, params={}):
        MitosisSteppableBase.__init__(self, frequency)
        self.CRIT_VOLUME = params["critVolume"]

    def step(self, mcs):
        cells_to_divide = []
        for cell in self.cell_list_by_type(self.CELLGROW):
            if cell.volume > self.CRIT_VOLUME:
                cells_to_divide.append(cell)

        for cell in cells_to_divide:
            self.divide_cell_random_orientation(cell)

    def update_attributes(self):
        self.parent_cell.targetVolume /= 2.0
        self.clone_parent_2_child()

        self.parent_cell.type = self.CELL
        self.child_cell.type = self.CELL
