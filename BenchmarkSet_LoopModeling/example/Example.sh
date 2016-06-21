#!/bin/bash

#### This example script runs all minimizations and scoring methods on one PDB ID, 1oyc.
## If you are running this, make sure to change the BASE_DIR variable in scripts 1., 2., 3., and 5.
## Also, in script 1., you must change the ROS_EXE variable to your Rosetta Executables path and the ROS_DB variable to you Rosetta database path.

BASE_DIR=$(dirname `pwd`)
SCRIPT_DIR=$BASE_DIR'/methods/'
OUTPUT_DIR=$BASE_DIR'/output/'

## Unzip the input archive - although you will only need the 1oyc files for running this example, you may as well unzip all of them.
7za loop_modeling_ngk_r57934.7z


## First, minimize in Rosetta. This runs the 1.Rosetta_Minimize script without automatic submission.
python $SCRIPT_DIR'/'1.Rosetta_Minimize.py 1oyc 0

## Therefore, one must cd into the 1oyc rosetta_minimization directory and run all bash scripts.
## *Note: the execution of the scripts occurs serially, and so will take forever. Feel free to change
## how the bashing takes place as best suits your system.
cd $OUTPUT_DIR'/rosetta_minimization/1oyc/'
for SCRIPT in `ls min*.sh`
    do
        bash $SCRIPT
    done

## Return to the working directory.
cd $BASE_DIR

## Set up the minimization parameters for 1oyc, while also making the amber_minimization/ directory
## and amber_minimization/1oyc/ directory.
python $SCRIPT_DIR'/'2.Amber_MinimizationSetUp.py 1oyc

## Generate the coordinate (.rst7) and topology (.parm7) file for 1oyc.
python $SCRIPT_DIR'/'3.Amber_GenerateRST7andParm7.py 1oyc

## Go into the amber_minimization/1oyc/ directory,
cd $OUTPUT_DIR'/amber_minimization/1oyc/'

## And run the Amber Minimization script, giving the topology file under the flag -p,
## the coordinates files as -c, and the minimization parameters as -i.
python $SCRIPT_DIR'/'4.Amber_RunMinimization.py -p 1oyc.parm7 \
    -O -c "NoH*.rst7" -i min.in

## Return to the working directory.
cd $BASE_DIR

## And get the Amber energies for all decoys in the /amber_minimization/1oyc/ directory, 
## while outputting the scorefile as /amber_minimization/1oyc/1oyc_amber.sc.
python $SCRIPT_DIR'/'5.Amber_GetEnergies.py -i 1oyc -o 1oyc_amber.sc
