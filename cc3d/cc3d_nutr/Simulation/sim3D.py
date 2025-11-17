import json
import sys

from cc3d import CompuCellSetup
from cc3d.core.XMLUtils import ElementCC3D
from sim3DSteppables import (ConstraintInitializerSteppable, GrowthSteppable,
                             MitosisSteppable)


def read_params(path_to_json):
    with open(path_to_json, "r") as file:
        return json.load(file)


def configure_simulation(filename, params, proc_num):
    ##############################PARAMS##############################
    # Init position
    # cellCenterX, cellCenterY, cellCenterZ = 32.0, 32.0, 32.0
    # cellRadius = 5.0
    # cellWidth = 7.0

    cellCenterX, cellCenterY, cellCenterZ = 32.0, 32.0, 32.0
    cellRadius = 14.0
    cellWidth = 5.0
    temp = params["temp"]

    # Simulation
    timesteps = params["timesteps"]
    ##############################PARAMS##############################

    from cc3d.core.XMLUtils import ElementCC3D
    CompuCell3DElmnt=ElementCC3D("CompuCell3D",{"Revision":"2","Version":"4.6.0"})

    MetadataElmnt = CompuCell3DElmnt.ElementCC3D("Metadata")

    # Basic properties simulation
    MetadataElmnt.ElementCC3D("NumberOfProcessors", {}, f"{proc_num}")
    MetadataElmnt.ElementCC3D("DebugOutputFrequency", {}, "10")
    PottsElmnt = CompuCell3DElmnt.ElementCC3D("Potts")

    # Basic properties of CPM (GGH) algorithm

    #CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=
    #PottsElmnt.ElementCC3D("Dimensions", {"x": "64", "y": "64", "z": "64"})
    PottsElmnt.ElementCC3D("Dimensions", {"x": "64", "y": "64", "z": "64"})
    PottsElmnt.ElementCC3D("Steps", {}, f"{timesteps}")
    PottsElmnt.ElementCC3D("Temperature", {}, f"{temp}")
    PottsElmnt.ElementCC3D("NeighborOrder", {}, "1")
    PluginElmnt = CompuCell3DElmnt.ElementCC3D("Plugin", {"Name": "CellType"})


    #CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=
    # Listing all cell types in the simulation
    PluginElmnt.ElementCC3D("CellType", {"TypeId": "0", "TypeName": "Medium"})
    PluginElmnt.ElementCC3D("CellType", {"TypeId": "1", "TypeName": "cell"})
    PluginElmnt.ElementCC3D("CellType", {"TypeId": "2", "TypeName": "cellHypo"})
    PluginElmnt.ElementCC3D("CellType", {"TypeId": "3", "TypeName": "cellDead"})
    PluginElmnt.ElementCC3D("CellType", {"TypeId": "4", "TypeName": "cellGrow"})


    #CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=
    CompuCell3DElmnt.ElementCC3D("Plugin", {"Name": "Volume"})
    CompuCell3DElmnt.ElementCC3D("Plugin", {"Name": "Surface"})
    PluginElmnt_1 = CompuCell3DElmnt.ElementCC3D("Plugin", {"Name": "CenterOfMass"})



    #CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=
    # Module tracking center of mass of each cell
    PluginElmnt_2 = CompuCell3DElmnt.ElementCC3D("Plugin", {"Name": "NeighborTracker"})

    #CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=
    # Module tracking neighboring cells of each cell
    PluginElmnt_3 = CompuCell3DElmnt.ElementCC3D("Plugin", {"Name": "PixelTracker"})

    #CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=CHECK=
    # Module tracking pixels of each cell
    PluginElmnt_4 = CompuCell3DElmnt.ElementCC3D("Plugin", {"Name": "BoundaryPixelTracker"})
    PluginElmnt_4.ElementCC3D("NeighborOrder", {}, "1")

    # Nutrition field values
    nutrFieldValue = params["nutrFieldValue"]
    initNutrValue = params["initNutrValue"]
    nutrDiffusion = params["nutrDiffusion"]
    nutrDecay = 0.0

    # Contact energy
    contactCM = params["contactCM"]
    contactCC = params["contactCC"]

    # Module tracking boundary pixels of each cell

    PluginElmnt_5 = CompuCell3DElmnt.ElementCC3D("Plugin", {"Name": "Contact"})
    # Specification of adhesion energies
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "Medium", "Type2": "Medium"}, "0.0")
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "Medium", "Type2": "cell"}, f"{contactCM}")
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "Medium", "Type2": "cellHypo"}, f"{contactCM}")
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "Medium", "Type2": "cellDead"}, f"{contactCM}")
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "Medium", "Type2": "cellGrow"}, f"{contactCM}")
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "cell", "Type2": "cell"}, f"{contactCC}")
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "cell", "Type2": "cellHypo"}, f"{contactCC}")
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "cell", "Type2": "cellDead"}, f"{contactCC}")
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "cell", "Type2": "cellGrow"}, f"{contactCC}")
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "cellHypo", "Type2": "cellHypo"}, f"{contactCC}")
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "cellHypo", "Type2": "cellDead"}, f"{contactCC}")
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "cellHypo", "Type2": "cellGrow"}, f"{contactCC}")
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "cellDead", "Type2": "cellDead"}, f"{contactCC}")
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "cellDead", "Type2": "cellGrow"}, f"{contactCC}")
    PluginElmnt_5.ElementCC3D("Energy", {"Type1": "cellGrow", "Type2": "cellGrow"}, f"{contactCC}"    )
    PluginElmnt_5.ElementCC3D("NeighborOrder", {}, "4")

    PluginElmnt_6 = CompuCell3DElmnt.ElementCC3D("Plugin", {"Name": "Secretion"})

    # Specification of secretion properties of select cell types.
    # You may repeat Field element for each chemical field declared in the PDE solvers
    # Specification of secretion properties of individual cells can be done in Python

    SteppableElmnt = CompuCell3DElmnt.ElementCC3D("Steppable", {"Type": "DiffusionSolverFE"})

    # Specification of PDE solvers
    DiffusionFieldElmnt = SteppableElmnt.ElementCC3D("DiffusionField", {"Name": "nutr"})
    DiffusionDataElmnt = DiffusionFieldElmnt.ElementCC3D("DiffusionData")
    DiffusionDataElmnt.ElementCC3D("FieldName", {}, "nutr")
    DiffusionDataElmnt.ElementCC3D("GlobalDiffusionConstant", {}, f"{nutrDiffusion}")
    DiffusionDataElmnt.ElementCC3D("GlobalDecayConstant", {}, f"{nutrDecay}")
    # Additional options are:
    DiffusionDataElmnt.ElementCC3D("InitialConcentrationExpression", {}, f"{initNutrValue}")
    # DiffusionDataElmnt.ElementCC3D("InitialConcentrationExpression", {}, f"0.1 + 0.05*sin(x/10.0) * cos(y/15.0)")

    BoundaryConditionsElmnt = DiffusionFieldElmnt.ElementCC3D("BoundaryConditions")
    PlaneElmnt = BoundaryConditionsElmnt.ElementCC3D("Plane", {"Axis": "X"})
    PlaneElmnt.ElementCC3D("ConstantValue", {"PlanePosition": "Min", "Value": f"{nutrFieldValue}"})
    PlaneElmnt.ElementCC3D("ConstantValue", {"PlanePosition": "Max", "Value": f"{nutrFieldValue}"})
    # Other options are (examples):
    # PlaneElmnt.ElementCC3D("Periodic")
    # PlaneElmnt.ElementCC3D("ConstantDerivative",{"PlanePosition":"Min","Value":"10.0"})

    PlaneElmnt_1 = BoundaryConditionsElmnt.ElementCC3D("Plane", {"Axis": "Y"})
    PlaneElmnt_1.ElementCC3D("ConstantValue", {"PlanePosition": "Min", "Value": f"{nutrFieldValue}"})
    PlaneElmnt_1.ElementCC3D("ConstantValue", {"PlanePosition": "Max", "Value": f"{nutrFieldValue}"})
    # Other options are (examples):
    # PlaneElmnt_1.ElementCC3D("Periodic")
    # PlaneElmnt_1.ElementCC3D("ConstantValue",{"PlanePosition":"Min","Value":"10.0"})

    PlaneElmnt_2 = BoundaryConditionsElmnt.ElementCC3D("Plane", {"Axis": "Z"})
    PlaneElmnt_2.ElementCC3D("ConstantValue", {"PlanePosition": "Min", "Value": f"{nutrFieldValue}"})
    PlaneElmnt_2.ElementCC3D("ConstantValue", {"PlanePosition": "Max", "Value": f"{nutrFieldValue}"})
    # Other options are (examples):
    # PlaneElmnt_2.ElementCC3D("Periodic")
    # PlaneElmnt_2.ElementCC3D("ConstantValue",{"PlanePosition":"Min","Value":"10.0"})


    # Initial layout of cells in the form of spherical (circular in 2D) blob
    SteppableElmnt_1 = CompuCell3DElmnt.ElementCC3D("Steppable", {"Type": "BlobInitializer"})
    RegionElmnt = SteppableElmnt_1.ElementCC3D("Region")
    RegionElmnt.ElementCC3D("Center", {"x": f"{cellCenterX}", "y": f"{cellCenterY}", "z": f"{cellCenterZ}"} )
    RegionElmnt.ElementCC3D("Radius", {}, f"{cellRadius}")
    RegionElmnt.ElementCC3D("Gap", {}, "0")
    RegionElmnt.ElementCC3D("Width", {}, f"{cellWidth}")
    RegionElmnt.ElementCC3D("Types", {}, "cell")
    CompuCellSetup.setSimulationXMLDescription(CompuCell3DElmnt)

    CompuCellSetup.setSimulationXMLDescription(CompuCell3DElmnt)


# READ PARAMS
params = {
            "nutrFieldValue": 1.2,
            "initNutrValue": 1.2,
            "nutrDiffusion": 0,
            "contactCM": 30.0,
            "contactCC": 10.0,
            "temp": 30.0,
            "timesteps": 155,
            "targetVolume": 110,
            "lambdaVolume": 2.0,
            "ratio": 2.0,
            "lambdaSurface": 1.0,
            "concentraion_min": 1.0,
            "concentraion_max": 1.1,
            "cellUptake": 0.01,
            "cellUptakeRelative": 0.01,
            "timeToDeath": 50,
            "deltaDeath": 3.1,
            "deltaVolume": 2.0,
            "critVolume": 150,
            "dump_time": 50,
        }


# START SIMULATION

# define simulation name
sim_name = "data_3"
configure_simulation(sim_name, params, 1)


CompuCellSetup.register_steppable(
    steppable=ConstraintInitializerSteppable(frequency=1, params=params)
)

CompuCellSetup.register_steppable(
    steppable=GrowthSteppable(frequency=1, sim_name=sim_name, params=params)
)

CompuCellSetup.register_steppable(
    steppable=MitosisSteppable(frequency=1, params=params)
)

CompuCellSetup.run()
