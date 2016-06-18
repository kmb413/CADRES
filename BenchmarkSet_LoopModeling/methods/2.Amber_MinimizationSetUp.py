#!/usr/bin/env python

import os, sys
import pandas as pd

##### Directories and Paths ##### TODO: CHANGE
BASE_DIR    =  "/scratch/kmb413/CADRES/BenchmarkSet_LoopModeling/methods"
NATIVES_DIR =  "{base_directory}/Natives".format( base_directory=BASE_DIR )
DECOY_DIR   =  "{base_directory}/loop_modeling_ngk_r57934/r57934/talaris2014/job_output".format( base_directory=BASE_DIR )

try:
    os.mkdir('{base_directory}/amber_minimization'.format( base_directory=BASE_DIR ) )
except OSError:
    pass
##########################


## Read in Loop Definitions
loopdef = pd.read_json('loopdefs.json')

## Define minimization parameters
mdin_template = """
&cntrl
    imin = 1, maxcyc=1000,
    ntx = 1,
    ntxo = 2,
    ntwr = 100, ntpr = 100,
    cut = 999.0,
    ntb = 0, igb = 8,
    ntr = 1, 
    restraint_wt = 10,
    restraintmask = "!:{loop_start}-{loop_end} & !@H=",
    ntmin=3, drms=0.01,
/
"""

## For all PDBs in the loopdefs file, prepare minimization scripts for ELF1 submission.
def main(pdblist):
    for code in pdblist:
        print("PDB Code: {}".format(code))

        ## Gather the loop data.
        loop_end = loopdef[code]['EndResidueID'].strip()
        loop_start = loopdef[code]['StartResidueID'].strip()

        ## Change to the directory where the scrips will be made.
        if not os.path.exists('{base_directory}/amber_minimization/{PDB}'.format( base_directory=BASE_DIR, PDB=code ) ):
            os.mkdir('{base_directory}/amber_minimization/{PDB}'.format( base_directory=BASE_DIR, PDB=code ) )

        os.chdir('{base_directory}/amber_minimization/{PDB}'.format(base_directory=BASE_DIR, PDB=code))

        ## Write a minimization parameters file, substituting the loop data where necessary.
        with open('min.in', 'w') as fh:
            mdin = mdin_template.format(loop_start=loop_start, loop_end=loop_end)
            fh.write(mdin)

if __name__ == '__main__':
    pdblist_ = sys.argv[1]

    if os.path.isfile(pdblist_):
        with open(pdblist_) as fh:
            PDBLIST = fh.read().split()
    else:
        PDBLIST = pdblist_.split(',')

    main(pdblist=PDBLIST)
