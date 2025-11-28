 #!/bin/bash


blockMesh -case ../OpenFoamProject
snappyHexMesh -overwrite -case ../OpenFoamProject
foamCleanCase -case ../OpenFoamProject
source /home/softmatter/CompuCell3D/miniconda3/bin/activate
source /home/softmatter/OPENFOAM/OpenFOAM-10/etc/bashrc
