#!/bin/bash

pdb=$1
actual_fn=$2 
pdb_name=$3
pdb_final_outpath=$4


#find all pdb files in this directory and put them in a list
cd $pdb'/'
find `pwd`/*.pdb -maxdepth 0 > list.txt

#find native name
native=$INPATH'/input_pdbs/'${actual_fn:0:6}'_complex.pdb'

log_name="ddg_rmsd.log"

#check that log didn't finish successfully
grep -sq "reported success" $log_name
if [ $? -gt 0 ];
then
       nohup nice $ROSETTA_BIN'/'rosetta_scripts.static.linuxgccrelease -database $ROSETTA_DB -ex1 -ex2 -extrachi_cutoff 1 -use_input_sc -l list.txt -parser:protocol ~/CADRES/PDZ_ddG/xml/ddg_rmsd.xml -in:file:native $native -score:weights talaris2014_cst > $log_name 
       rm *_00??_0001.pdb
fi

awk -v OFS=',' ' NR != 1 && NR != 2 {print $NF,$6,$(NF-1)}' score.sc > $pdb_final_outpath'/'$actual_fn'.csv'
