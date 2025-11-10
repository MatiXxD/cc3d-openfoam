
def configure_simulation():

    from cc3d.core.XMLUtils import ElementCC3D

    CompuCell3DElmnt=ElementCC3D("CompuCell3D",{"Revision":"2","Version":"4.6.0"})

    MetadataElmnt=CompuCell3DElmnt.ElementCC3D("Metadata")

    # Basic properties simulation
    MetadataElmnt.ElementCC3D("NumberOfProcessors",{},"1")
    MetadataElmnt.ElementCC3D("DebugOutputFrequency",{},"10")
    # MetadataElmnt.ElementCC3D("NonParallelModule",{"Name":"Potts"})

    PottsElmnt=CompuCell3DElmnt.ElementCC3D("Potts")

    # Basic properties of CPM (GGH) algorithm
    PottsElmnt.ElementCC3D("Dimensions",{"x":"64","y":"64","z":"64"})
    PottsElmnt.ElementCC3D("Steps",{},"10000")
    PottsElmnt.ElementCC3D("Temperature",{},"10.0")
    PottsElmnt.ElementCC3D("NeighborOrder",{},"1")

    PluginElmnt=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"CellType"})

    # Listing all cell types in the simulation
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"0","TypeName":"Medium"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"1","TypeName":"cell1"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"2","TypeName":"cell2"})

    CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"Volume"})

    CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"Surface"})

    PluginElmnt_1=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"CenterOfMass"})

    # Module tracking center of mass of each cell

    PluginElmnt_2=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"NeighborTracker"})

    # Module tracking neighboring cells of each cell

    PluginElmnt_4=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"BoundaryPixelTracker"})

    # Module tracking neighboring cells of each cell

    PluginElmnt_3=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"Contact"})
    # Specification of adhesion energies
    PluginElmnt_3.ElementCC3D("Energy",{"Type1":"Medium","Type2":"Medium"},"10.0")
    PluginElmnt_3.ElementCC3D("Energy",{"Type1":"Medium","Type2":"cell1"},"10.0")
    PluginElmnt_3.ElementCC3D("Energy",{"Type1":"Medium","Type2":"cell2"},"10.0")
    PluginElmnt_3.ElementCC3D("Energy",{"Type1":"cell1","Type2":"cell1"},"10.0")
    PluginElmnt_3.ElementCC3D("Energy",{"Type1":"cell1","Type2":"cell2"},"10.0")
    PluginElmnt_3.ElementCC3D("Energy",{"Type1":"cell2","Type2":"cell2"},"10.0")
    PluginElmnt_3.ElementCC3D("NeighborOrder",{},"4")

    SteppableElmnt=CompuCell3DElmnt.ElementCC3D("Steppable",{"Type":"UniformInitializer"})

    # Initial layout of cells in the form of rectangular slab
    RegionElmnt=SteppableElmnt.ElementCC3D("Region")
    RegionElmnt.ElementCC3D("BoxMin",{"x":"12","y":"12","z":"12"})
    RegionElmnt.ElementCC3D("BoxMax",{"x":"51","y":"51","z":"51"})
    RegionElmnt.ElementCC3D("Gap",{},"0")
    RegionElmnt.ElementCC3D("Width",{},"7")
    RegionElmnt.ElementCC3D("Types",{},"cell1,cell2")

    CompuCellSetup.setSimulationXMLDescription(CompuCell3DElmnt)
    CompuCellSetup.setSimulationXMLDescription(CompuCell3DElmnt)


# setup simulation using python
from cc3d import CompuCellSetup
configure_simulation()


# default steppables
from cc3d_integration_steppables import ConstraintInitializerSteppable
CompuCellSetup.register_steppable(steppable=ConstraintInitializerSteppable(frequency=1))

from cc3d_integration_steppables import GrowthSteppable
CompuCellSetup.register_steppable(steppable=GrowthSteppable(frequency=1))


# custom steppable
from cc3d_integration_steppables import PixelTrackerSteppable
CompuCellSetup.register_steppable(steppable=PixelTrackerSteppable(frequency=1))


# run simulation
CompuCellSetup.run()
