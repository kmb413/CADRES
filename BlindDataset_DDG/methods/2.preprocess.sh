#!/bin/bash

pdb=$1
actual_fn=$2 
pdb_name=$3
pdb_final_outpath=$4
cst_param=$5

cd $pdb_final_outpath

if [[ ! $actual_fn =~ ^[0-9a-z]{4}_ && ! $actual_fn =~ ^[0-9a-z]{4}$ ]]
then
        echo "This is a generated file, no need to preprocess, skipping"
        exit
fi
        
python $SCRIPTS'/'gen_mutfile_pdbs.py --in_pdb $pdb --orig_pdb_path  $INPATH'/'input_pdbs/orig_pdb/ --list_seqs_file $INPATH'/'list_seqs'/'$pdb_name'.list' --all_seqs_data $INPATH'/'list_seqs'/'all_seqs_data.tsv --mut_file_path $INPATH'/'mut_file'/'
