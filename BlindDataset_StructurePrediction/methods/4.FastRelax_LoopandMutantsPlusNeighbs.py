import os
#from glob import glob

#decoy_list = glob('/scratch/kmb413/Blind_Tests/3.StructurePrediction/PartOne/3.mutate_kicloop/*.pdb')

ROS_EXE="/home/kmb413/RealRosetta/Rosetta/main/source/bin/rosetta_scripts.linuxclangrelease"
ROS_DB="/home/kmb413/RealRosetta/Rosetta/main/database"
BASE_DIR=/scratch/kmb413/CADRES/BlindDataset_StructurePrediction/
SCRIPTS_DIR="{base}/scripts/".format( base=BASE_DIR )
OUTPUT_DIR="{base}/work/FastRelax_LoopandMutantsPlusNeighbs/".format( base=BASE_DIR )

try:
    os.mkdir( OUTPUT_DIR )
except OSError:
    pass
os.chdir( OUTPUT_DIR )

input_file = glob.glob('{base}/work/make_allala/*.pdb'.format( base=BASE_DIR ))[0] #should only be one file
best_relaxed = os.path.splitext(os.path.basename(input_file))[0]

for i in range(1,41):
    #header = "#!/bin/bash\n#SBATCH -n 1\n#SBATCH -c 1\n#SBATCH -o decoy_{count}.out\n#SBATCH --job-name={count}\n".format(count=i)

    with open('fastrelax{count}.sh'.format(count=i), 'w') as script:
        for j in range(1,26):
            jnum = str(j)
            if len(jnum) < 2:
                jnum = '0'+jnum
            command = "{ros_exe} -database {ros_db} -parser:protocol {scripts}/xmls/fastrelax_kicloop.xml -in:file:s {base}/work/ThreadSeq_and_RemodelLoop/{best}_{count}_00{jnum}.pdb @/{scripts}/xmls/flagsfile -out:file:scorefile fastrelaxed_{count}.sc -nstruct 5\n".format(ros_exe=ROS_EXE, ros_db=ROS_DB, base=BASE_DIR, scripts=SCRIPTS_DIR, best=best_relaxed, count=i, jnum=jnum)

            script.write(command)

    os.system('bash fastrelax{count}.sh &'.format(count=i) )
