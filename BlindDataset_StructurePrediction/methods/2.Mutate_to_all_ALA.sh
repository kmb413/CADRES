ROS_EXE=/home/kmb413/RealRosetta/Rosetta/main/source/bin/rosetta_scripts.static.linuxgccrelease
ROS_DB=/home/kmb413/RealRosetta/Rosetta/main/database
BASE_DIR=/scratch/kmb413/CADRES/BlindDataset_StructurePrediction/
SCRIPTS_DIR=$BASE_DIR'/scripts/'
INPUT_DIR=$BASE_DIR'/input/'
OUTPUT_DIR=$BASE_DIR'/work/make_allala/'

cd $BASE_DIR'/work/fastrelax_init/'

lowest_name=$( tail -n +3 score_fastrelax_initial.sc | sort -nk 2 | head -n 1 | awk '{print $NF}' ) 

cd $OUTPUT_DIR
$ROS_EXE -database $ROS_DB -parser:protocol $SCRIPTS_DIR/xmls/make_allala.xml -in:file:s $BASE_DIR'/work/fastrelax_init/'$lowest_name'.pdb' -out:file:scorefile allala.sc -parser:script_vars all_ala=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASADHETLEINAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA > allala.log
