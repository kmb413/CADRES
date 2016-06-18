import os

BASE_DIR="/scratch/kmb413/CADRES/BlindDataset_StructurePrediction/methods"
ROS_EXE="/home/kmb413/RealRosetta/Rosetta/main/source/bin/rosetta_scripts.static.linuxgccrelease"
ROS_DB="/home/kmb413/RealRosetta/Rosetta/main/database"

input_file = '{base}/1igs_0001_0037_0001.pdb'.format( base=BASE_DIR )
seq = 'PRYLKGWLKDVVQLSLRRPSFRASRQRPIISLNERILEFNKRNITAIIAEYKRKSPSGLDVERDPIEYSKFMERYAVGLSILTEEKYFNGSYETLRKIASSVSIPILMADFIVKESQIDDAYNLGADTVLLIVKILTERELESLLEYARSYGMEPLIGINDENDLDIALRIGARFIGIHSADHETLEINKENQRKLISMIPSNVVKVAAHGISERNEIEELRKLGVNAFLIGSSLMRNPEKIKEFIL'

try:
    os.mkdir('{base}/3.RemodelLoop_ThreadSeq/'.format( base=BASE_DIR )
except OSError:
    pass

os.chdir('{base}/3.RemodelLoop_ThreadSeq/'.format( base=BASE_DIR )

for i in range(1,41):
    header = "#!/bin/bash\n#SBATCH -n 1\n#SBATCH -c 1\n#SBATCH -o decoy_{count}.out\n#SBATCH --job-name={count}\n".format(count=i)
    command = "{ros_exe} -database {ros_db} -parser:protocol {base}/xmls/mutate_kicloop.xml -in:file:s {best_fastrelaxed_allala} @{base}/xmls/flagsfile -out:file:scorefile decoy_{count}.sc -nstruct 25 -out:suffix _{count} -parser:script_vars real_seq={sequence}".format(ros_exe=ROS_EXE, ros_db=ROS_DB, base=BASE_DIR, count=i, best_fastrelaxed_allala=input_file, sequence=seq)

    with open('decoy_{count}.sh'.format(count=i), 'w') as script:
        #script.write(header)
        script.write(command)

    os.system('bash decoy_{count}.sh &'.format(count=i))
