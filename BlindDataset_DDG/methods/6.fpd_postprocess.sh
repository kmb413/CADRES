#!/bin/bash

pdb=$1
actual_fn=$2 
pdb_name=$3
pdb_final_outpath=$4
cst_file=$5
server=$6

#check that there are subdirectories in this folder
ls -l | grep -sq '^d'
if [ $? -gt 0 ];
then 

	python $SCRIPTS'/'select_fpd_results.py --path_prefix $pdb'/'

fi
