import os
from glob import glob

AMBER_SOURCE="/scratch/kmb413/amber_jan142016/amber.sh"
BASE_DIR=/scratch/kmb413/CADRES/BlindDataset_StructurePrediction/
SCRIPTS_DIR="{base}/scripts/".format( base=BASE_DIR )
OUTPUT_DIR="{base}/work/AmberMinimize/".format( base=BASE_DIR )

try:
    os.mkdir( OUTPUT_DIR )
except OSError:
    pass

os.chdir( OUTPUT_DIR )

def chunks(l,n):
    n = max(1,n)
    return [l[i:i+n] for i in range(0, len(l), n)]

decoy_list = glob('{base}/work/FastRelax_LoopandMutantsPlusNeighbs/*.pdb'.format( base=BASE_DIR ) )
chunk_list = chunks(decoy_list, 20)

for pdb_chunk in range(len(chunk_list)):
    header = "#!/bin/bash\n#SBATCH -n 1\n#SBATCH -c 1\n#SBATCH -o decoybatch_{count}.out\n#SBATCH --job-name={count}\n\nsource {amber}\n\n".format(count=pdb_chunk, amber=AMBER_SOURCE)
    
    with open('minbatch_{count}.sh'.format(count=pdb_chunk), 'w') as script:
        
        #script.write(header)
    
        for pdb in chunk_list[pdb_chunk]:
            os.system("sed '/     H  /d' {pdb} > NoH_{pdbname}".format(pdb=pdb, pdbname=pdb.split('/')[-1]) )
            
            with open('tleap.in','w') as tfile:
                tfile.write("source leaprc.protein.ff14SBonlysc\n")
                tfile.write("m = loadpdb NoH_{pdbname}\n".format(pdbname=pdb.split('/')[-1]))
                tfile.write("set default pbradii mbondi3\n")
                tfile.write("saveamberparm m decoy.parm7 {pdbname}.rst7\n".format(pdbname=pdb.split('/')[-1]))
                tfile.write("quit")
            os.system('tleap -f tleap.in')
            
            command = "sander -i {scripts}/min_norestraint.in -o {pdbname}.out -p decoy.parm7 -c {pdbname}.rst7 -r min_{pdbname}.rst7 -ref {pdbname}.rst7\n".format( scripts=SCRIPTS_DIR, pdbname=pdb.split('/')[-1])
            script.write(command)

    os.system('bash minbatch_{count}.sh &'.format(count=pdb_chunk) )
