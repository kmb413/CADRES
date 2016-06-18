#!/usr/bin/env python

import os, sys
import pandas as pd
from glob import glob

##### Directories and Paths ##### 
BASE_DIR    =  "/scratch/kmb413/CADRES/BenchmarkSet_LoopModeling/methods"
NATIVES_DIR =  "{base_directory}/Natives".format( base_directory=BASE_DIR )
DECOY_DIR   =  "{base_directory}/loop_modeling_ngk_r57934/r57934/talaris2014/job_output".format( base_directory=BASE_DIR )

try:
    os.mkdir('{base_directory}/rosetta_minimization'.format( base_directory=BASE_DIR ) )
except OSError:
    pass

ROS_EXE =  "/home/kmb413/RealRosetta/Rosetta/main/source/bin/rosetta_scripts.static.linuxgccrelease"
ROS_DB  =  "/home/kmb413/RealRosetta/Rosetta/main/database"
XML = "{base_directory}/RosettaMin.xml".format( base_directory=BASE_DIR )
#######################

##### Functions #######
def chunks(l,n):
    n = max(1,n)
    return [l[i:i+n] for i in range(0, len(l), n)]
#######################


## Read in Loop Definitions
loopdef = pd.read_json('loopdefs.json')

def main(pdblist, auto_submit):
    ## For all PDBs in the loopdefs file, prepare minimization scripts for Slurm submission.
    for code in pdblist: 
        print("PDB Code: {}".format(code))

        ## Gather the loop data.
        loop_end = loopdef[code]['EndResidueID'].strip()
        loop_start = loopdef[code]['StartResidueID'].strip()

        ## Get the cleaned, native PDB for RMSD.
        native = '{natives_directory}/{PDB}.clean.pdb'.format(natives_directory=NATIVES_DIR, PDB=code)

        ## Change to the directory where the scripts will be made.
        #if not os.path.exists('{base_directory}/rosetta_minimization/{PDB}'.format( base_directory=BASE_DIR, PDB=code ) ):
        #    os.mkdir('{base_directory}/rosetta_minimization/{PDB}'.format( base_directory=BASE_DIR, PDB=code ) )
        try:
            os.mkdir('{base_directory}/rosetta_minimization/{PDB}'.format( base_directory=BASE_DIR, PDB=code ) )
        except OSError:
            pass
        
        os.chdir('{base_directory}/rosetta_minimization/{PDB}'.format(base_directory=BASE_DIR, PDB=code))

        ## Make a list of all PDBs in the Decoy Directory under this PDB code.
        decoylist = glob('{decoy_directory}/{PDB}*.pdb'.format(decoy_directory=DECOY_DIR, PDB=code))
        print("Number of decoy structures to minimize: "+str(len(decoylist)))

        ## Divide the list a list of sublists where each sublist has at most 100 decoys.
        decoy_chunks = chunks( decoylist, 100 )

        ## For each sublist, make a minimization script.
        chunk_num = 0
        for chunk in decoy_chunks:
            chunk_num += 1

            ## Write all PDBs in the sublist to a list file.
            with open('{PDB}.{count}.list'.format(PDB=code, count=chunk_num), 'w') as chunkfile:
                for decoy in chunk:
                    chunkfile.write(decoy+'\n')

            ## Write a Slurm-style header and the Rosetta minimization command to the bash script.
            with open('min.{count}.sh'.format(count=chunk_num),'w') as minfile:
                
                minfile.write("#!/bin/bash\n#SBATCH -n 1\n#SBATCH -c 1\n#SBATCH -o {PDB}_{count}.out\n#SBATCH --job-name={PDB}_{count}\n".format( PDB=code, count=chunk_num ))
                
                minfile.write("{rosetta_executable} -database {rosetta_database} -l {PDB}.{count}.list -parser:protocol {xml_path} -in:file:native {native_pdb} -score:weights talaris2014 -ex1 -ex2 -extrachi_cutoff 1 -use_input_sc -nblist_autoupdate -out:file:scorefile score.{count}.sc -parser:script_vars loop_start_pre={lsp} loop_start={ls} loop_end={le}".format( rosetta_executable=ROS_EXE, rosetta_database=ROS_DB, PDB=code, count=chunk_num, xml_path=XML, native_pdb=native, lsp=(int(loop_start)-1), ls=loop_start, le=loop_end ))

            ## Submit each bash script to the job queue.
            if auto_submit == 1:
                os.system('sbatch min.{count}.sh'.format(count=chunk_num))

if __name__ == '__main__':
    pdblist_ = sys.argv[1]
    
    submit = 1
    if  len(sys.argv) > 2:
        submit = sys.argv[2]

    if os.path.isfile(pdblist_):
        with open(pdblist_) as fh:
            PDBLIST = fh.read().split()
    else:
        PDBLIST = pdblist_.split(',')

    main(pdblist=PDBLIST, auto_submit=submit)
