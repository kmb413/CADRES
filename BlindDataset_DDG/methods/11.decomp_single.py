#!/usr/bin/evn python

import os, subprocess

def main(pdb_folder_dir):
    """

    Parameters
    pdb_folder_dir : str, directory having min_NoH_*rst7 and prmtop files
    """
    
    command = "MMPBSA.py -i ../mmgbsa.in -cp ../{root}/{pdb_folder}/prmtop -y ../{root}/{pdb_folder}/no_restraint_new_protocol/min_NoH_*rst7"

    pdb_folder = os.path.basename(pdb_folder_dir)
    root = os.path.dirname(pdb_folder_dir)

    try:
        os.mkdir(pdb_folder)
    except OSError:
        pass

    os.chdir(pdb_folder)
    print('processing {}'.format(pdb_folder))
    subprocess.check_call(command.format(pdb_folder=pdb_folder, root=root).split())

if __name__ == '__main__':
    import sys
    pdb_folder_dir = sys.argv[1]
    main(pdb_folder_dir)
