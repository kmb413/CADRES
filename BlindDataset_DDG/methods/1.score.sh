#!/bin/bash

pdb=$1
actual_fn=$2 
pdb_name=$3
pdb_final_outpath=$4
cst_param=$5

cd $pdb_final_outpath

if [[ ! $actual_fn =~ ^[0-9a-z]{4}_ && ! $actual_fn =~ ^[0-9a-z]{4}$ ]]
then
	echo "This is a generated file, no need to score, skipping"
	exit
fi    
    
$ROSETTA_BIN'/'score_jd2.default.linuxgccrelease -database $ROSETTA_DB -renumber_pdb -ignore_unrecognized_res -s $pdb -overwrite -out:pdb > $actual_fn'_score.log'

indir=$(dirname "$pdb")

mkdir -p $indir'/orig_pdb/'

if [ ! -f $indir'/orig_pdb/'$actual_fn'.pdb' ]
then
    mv $pdb $indir'/orig_pdb/'
fi
mv $indir'/'$actual_fn'_0001.pdb' $indir'/'$actual_fn'.pdb' 
