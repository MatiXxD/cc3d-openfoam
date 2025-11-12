from cc3d.core.PySteppables import *
import numpy as np
import time


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
            
            
class DumpSteppable(SteppableBasePy):
    dir = "/home/softmatter/Documents/CC3D-OF/cc3d-openfoam/cc3d/example_dumper/Simulation/dumps/"
    basename = "dump"
    dump_time = 100

    def __init__(self,frequency=1):
        SteppableBasePy.__init__(self, frequency)

    def start(self):
        ts = int(time.time())
        self.filename = self.dir + self.basename + f"_{ts}.dat"
        print("Open dump file...", self.filename)
        self.file = open(self.filename, "w")

    def step(self, mcs):
        if mcs % self.dump_time != 0:
            return

        print("Write to dump file")
        self._write_header(mcs)
        for x in range(self.dim.x):
            for y in range(self.dim.y):
                for z in range(self.dim.z):
                    cell_type = 0
                    cell = self.cell_field[x, y, z]
                    if cell:
                        cell_type = cell.type
                    self.file.write(f"{x} {y} {z} {cell_type}\n")
        self.file.write(f"\n\n\n\n\n")


    def _write_header(self, mcs):
        self.file.write(f"TIMESTEP: {mcs}\n")
        self.file.write(f"FORMAT: x y z type\n")
