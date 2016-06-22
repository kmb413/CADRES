#!/bin/bash

pdb=$1
actual_fn=$2
pdb_name=$3

cd $pdb
ls *.pdb > list
nohup nice $ROSETTA_BIN'/'FlexPepDocking.static.linuxgccrelease -database $ROSETTA_DB -l list -flexpep_score_only -score:weights ~/Rosetta/main/database/scoring/weights/talaris2014_cst.wts
awk '{ sum += $6+$38; n++ } END { if (n > 0) print sum / n; }' score.sc > $OUTPATH'/'ddg_csv/rosetta_inter_mean'/'$actual_fn'.txt'
nohup nice $ROSETTA_BIN'/'rosetta_scripts.static.linuxgccrelease -l list -use_input_sc -database $ROSETTA_DB -parser:protocol $SCRIPTS'/xmls/Interfaceselector.xml' -parser:script_vars chain1=A chain2=B -overwrite | grep "pymol" >> list_of_neighbors.txt
$SCRIPTS'/'get_average_amber_energy.pl res.csv list_of_neighbors.txt > $OUTPATH'/'ddg_csv/amber_inter_mean'/'$actual_fn'.txt'
