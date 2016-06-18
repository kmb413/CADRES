#### This example script runs all minimizations and scoring methods on one PDB ID, 1oyc.
## If you are running this, make sure to change the BASE_DIR variable in scripts 1., 2., 3., and 5.
## Also, in script 1., you must change the ROS_EXE variable to your Rosetta Executables path and the ROS_DB variable to you Rosetta database path.

## First, minimize in Rosetta. This runs the 1.Rosetta_Minimize script without automatic submission.
python 1.Rosetta_Minimize.py 1oyc 0

## Therefore, one must cd into the 1oyc rosetta_minimization directory and run all bash scripts.
## *Note: the execution of the scripts occurs serially, and so will take forever. Feel free to change
## how the bashing takes place as best suits your system.
cd rosetta_minimization/1oyc/
for SCRIPT in `ls min*.sh`
    do
        bash $SCRIPT
    done

## Return to the working directory.
cd ../../

## Set up the minimization parameters for 1oyc, while also making the amber_minimization/ directory
## and amber_minimization/1oyc/ directory.
python 2.Amber_MinimizationSetUp.py 1oyc

## Generate the coordinate (.rst7) and topology (.parm7) file for 1oyc.
python 3.Amber_GenerateRST7andParm7.py 1oyc

## Go into the amber_minimization/1oyc/ directory,
cd amber_minimization/1oyc

## And run the Amber Minimization script, giving the topology file under the flag -p,
## the coordinates files as -c, and the minimization parameters as -i.
python ../../4.Amber_RunMinimization.py -p 1oyc.parm7 \
    -O -c "NoH*.rst7" -i min.in

## Return to the working directory.
cd ../../

## And get the Amber energies for all decoys in the /amber_minimization/1oyc/ directory, 
## while outputting the scorefile as /amber_minimization/1oyc/1oyc_amber.sc.
python 5.Amber_GetEnergies.py -i 1oyc -o 1oyc_amber.sc
