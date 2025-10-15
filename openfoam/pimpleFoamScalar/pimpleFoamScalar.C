/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Copyright (C) 2011-2022 OpenFOAM Foundation
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/

#include "fvCFD.H"
#include "viscosityModel.H"
#include "incompressibleMomentumTransportModels.H"
#include "pimpleControl.H"
#include "pressureReference.H"
#include "CorrectPhi.H"
#include "fvModels.H"
#include "fvConstraints.H"
#include "localEulerDdtScheme.H"
#include "fvcSmooth.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    #include "postProcess.H"

    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "initContinuityErrs.H"
    #include "createDyMControls.H"
    #include "createFields.H"
    #include "createUfIfPresent.H"

    if (!LTS)
    {
        #include "CourantNo.H"
        #include "setInitialDeltaT.H"
    }

    Info<< "\nStarting time loop\n" << endl;

    while (pimple.run(runTime))
    {
        #include "readDyMControls.H"

        if (LTS)
        {
            #include "setRDeltaT.H"
        }
        else
        {
            #include "CourantNo.H"
            #include "setDeltaT.H"
        }

        fvModels.preUpdateMesh();

        // Update the mesh for topology change, mesh to mesh mapping
        mesh.update();

        runTime++;

        Info<< "Time = " << runTime.userTimeName() << nl << endl;

        // --- Pressure-velocity PIMPLE corrector loop
        while (pimple.loop())
        {
            if (pimple.firstPimpleIter() || moveMeshOuterCorrectors)
            {
                // Move the mesh
                mesh.move();

                if (mesh.changing())
                {
                    MRF.update();

                    if (correctPhi)
                    {
                        #include "correctPhi.H"
                    }

                    if (checkMeshCourantNo)
                    {
                        #include "meshCourantNo.H"
                    }
                }
            }

            fvModels.correct();

            #include "UEqn.H"

            // --- Pressure corrector loop
            while (pimple.correct())
            {
                #include "pEqn.H"
            }

            if (pimple.turbCorr())
            {
                viscosity->correct();
            }
        }

        // --- Scalar transport equation for T
        Info << "Assembling scalar transport equation for T at time " << runTime.userTimeName() << nl;

        // Собираем уравнение (транзиентное):
        // dT/dt + div(phi, T) - div(DT grad T) = 0
        // (если у вас есть source, можно добавить его вручную)
        fvScalarMatrix CEqn
        (
            fvm::ddt(C)
          + fvm::div(phi, C)
          - fvm::laplacian(DC, C)
        );

        // Применяем релаксацию (если задано в fvSolution)
        CEqn.relax();

        // При наличии fvConstraints (createFvConstraints.H)
        #ifdef USE_FVCONSTRAINTS
        fvConstraints.constrain(CEqn);
        #endif

        Info << "Solving for C..." << nl;

        // Решаем уравнение
        CEqn.solve();

        // Накладываем нижнюю границу: T >= 0
        C.max(0.0);

        // При наличии ограничений — наложить их на поле
        #ifdef USE_FVCONSTRAINTS
        fvConstraints.constrain(C);
        #endif

        Info << "C solved at time " << runTime.userTimeName() << nl;

        // Пишем результаты времени
        runTime.write();

        Info<< "ExecutionTime = " << runTime.elapsedCpuTime() << " s"
            << "  ClockTime = " << runTime.elapsedClockTime() << " s"
            << nl << endl;
    }

    Info<< "End\n" << endl;

    return 0;
}

// ************************************************************************* //

