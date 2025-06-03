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

class PixelTrackerSteppable(SteppableBasePy):
    dir = "/home/ilya/Work/border_detector/dumps/"
    basename = "dump"
    dump_time = 100
    border = None

    def __init__(self,frequency=1):
        SteppableBasePy.__init__(self, frequency)

    def start(self):
        self.boundary = np.zeros((self.dim.x, self.dim.y, self.dim.z))
        
        ts = int(time.time())
        self.filename = self.dir + self.basename + f"_{ts}.dat"
        print("Open dump file...", self.filename)
        self.file = open(self.filename, "w")

    def step(self, mcs):
        if mcs % self.dump_time != 0:
            return

        print("Write to dump file")
        self.boundary.fill(0) # clear prev boundary
        for cell in self.cell_list:
            boundary_pixels = self.get_cell_boundary_pixel_list(cell)
            for pixel_data in boundary_pixels:
                p = pixel_data.pixel
                self.boundary[p.x, p.y, p.z] = 1

        self._write_header(mcs)
        for x in range(self.dim.x):
            for y in range(self.dim.y):
                for z in range(self.dim.z):
                    self.file.write(f"{x} {y} {z} {self.boundary[x, y, z]}\n")
        self.file.write(f"\n\n")



    def _write_header(self, mcs):
        self.file.write(f"TIMESTEP: {mcs}\n")
        self.file.write(f"FORMAT: x y z is_border\n")
