import os
import glob

ROS_EXE="/home/kmb413/RealRosetta/Rosetta/main/source/bin/rosetta_scripts.static.linuxgccrelease"
ROS_DB="/home/kmb413/RealRosetta/Rosetta/main/database"
BASE_DIR=/scratch/kmb413/CADRES/BlindDataset_StructurePrediction/
SCRIPTS_DIR="{base}/scripts/".format( base=BASE_DIR )
OUTPUT_DIR="{base}/work/ThreadSeq_and_RemodelLoop/".format( base=BASE_DIR )

input_file = glob.glob('{base}/work/make_allala/*.pdb'.format( base=BASE_DIR ))[0] #should only be one file
seq = 'PRYLKGWLKDVVQLSLRRPSFRASRQRPIISLNERILEFNKRNITAIIAEYKRKSPSGLDVERDPIEYSKFMERYAVGLSILTEEKYFNGSYETLRKIASSVSIPILMADFIVKESQIDDAYNLGADTVLLIVKILTERELESLLEYARSYGMEPLIGINDENDLDIALRIGARFIGIHSADHETLEINKENQRKLISMIPSNVVKVAAHGISERNEIEELRKLGVNAFLIGSSLMRNPEKIKEFIL'

try:
    os.mkdir( OUTPUT_DIR )
except OSError:
    pass

os.chdir( OUTPUT_DIR )

for i in range(1,41):
    header = "#!/bin/bash\n#SBATCH -n 1\n#SBATCH -c 1\n#SBATCH -o decoy_{count}.out\n#SBATCH --job-name={count}\n".format(count=i)
    command = "{ros_exe} -database {ros_db} -parser:protocol {scripts}/xmls/mutate_kicloop.xml -in:file:s {best_fastrelaxed_allala} @{scripts}/xmls/flagsfile -out:file:scorefile decoy_{count}.sc -nstruct 25 -out:suffix _{count} -parser:script_vars real_seq={sequence}".format(ros_exe=ROS_EXE, ros_db=ROS_DB, base=BASE_DIR, scripts=SCRIPTS_DIR, count=i, best_fastrelaxed_allala=input_file, sequence=seq)

    with open('decoy_{count}.sh'.format(count=i), 'w') as script:
        #script.write(header)
        script.write(command)

    os.system('bash decoy_{count}.sh &'.format(count=i))
