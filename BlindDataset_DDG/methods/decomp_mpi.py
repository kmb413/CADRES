#!/usr/bin/evn python

import os
from mpi4py import MPI
import subprocess

comm = MPI.COMM_WORLD

def main(comm=comm):
    rank = comm.rank
    
    command = "MMPBSA.py -i ../mmgbsa.in -cp ../../{pdb_folder}/prmtop -y ../../{pdb_folder}/no_restraint_new_protocol/min_NoH_*rst7"
    pdblist = open('../pdblist.txt').read().split()
    pdb_folder = pdblist[rank]
    
    try:
        os.mkdir(pdb_folder)
    except OSError:
        pass

    os.chdir(pdb_folder)
    print('processing {}'.format(pdb_folder))
    subprocess.check_call(command.format(pdb_folder=pdb_folder).split())

if __name__ == '__main__':
    """mpirun -n 87 decomp_mpi.py
    # run mmgbsa decomp for each protein (50 structures)  in each core
    """

    main()
