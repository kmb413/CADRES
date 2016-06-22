#!/bin/bash

pdb=$1
actual_fn=$2 
pdb_name=$3
pdb_final_outpath=$4
cst_file=$5

cd $pdb_final_outpath

grep -sq "reported success" $actual_fn'_prepack.log'
if [ $? -gt 0 ];
then
        $ROSETTA_BIN'/'FlexPepDocking.linuxgccrelease -database $ROSETTA_DB -s $pdb -score:weights talaris2014_cst -out:prefix $actual_fn $cst_file -flexpep_prepack -ex1 -ex2 -use_input_sc > $actual_fn'_prepack.log'
fi

