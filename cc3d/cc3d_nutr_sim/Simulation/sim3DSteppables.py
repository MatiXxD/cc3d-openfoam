import numpy as np
from cc3d.core.PySteppables import *


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

    def get_surface(self, vol):
        return self.RATIO * (4 * np.pi * (3 * vol / (4.0 * np.pi)) ** (2.0 / 3.0))

    def init_files(self):
        self.filename += ".dat"
        with open(self.filename, "w") as f:
            pass

    def print_step(self, step):
        with open(self.filename, "a") as f:
            f.write(f"TIMESTEP {step}\n")
            f.write(f"x: 0 {self.dim.x}\n")
            f.write(f"y: 0 {self.dim.y}\n")
            f.write(f"z: 0 {self.dim.z}\n")
            f.write(f"cell_id cell_type pixel_x pixel_y pixel_z\n")

            for cell in self.cell_list:
                pixel_list = self.get_cell_pixel_list(cell)
                for pixel_tracker_data in pixel_list:
                    f.write(
                        f"{cell.id}  {cell.type} {pixel_tracker_data.pixel.x} {pixel_tracker_data.pixel.y} {pixel_tracker_data.pixel.z}\n"
                    )

    def step(self, mcs):
        secretor = self.get_field_secretor("nutr")
        nutrField = self.field.nutr

        # print("TEST", mcs)
        if mcs != 0 and (mcs % self.DUMP_TIME) == 0:
            print("STEP:", mcs)
            self.print_step(mcs)

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
            # Other valid options
            # self.divide_cell_orientation_vector_based(cell,1,1,0)
            # self.divide_cell_along_major_axis(cell)
            # self.divide_cell_along_minor_axis(cell)

    def update_attributes(self):
        self.parent_cell.targetVolume /= 2.0
        self.clone_parent_2_child()

        self.parent_cell.type = self.CELL
        self.child_cell.type = self.CELL
