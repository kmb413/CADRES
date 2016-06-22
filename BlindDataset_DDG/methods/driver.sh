#!/bin/bash

#driver script for PDZ ddG program
#first step is to preminimize sidechains and backbones of both complexes (primarily so that we can generate constraints files for xtal structures)

server=$1 #if only running with one server, make the server number be 1
prelim=$2

export HOME=~/
export ROSETTA_BIN=~/Rosetta/main/source/bin/
export ROSETTA_SRC=~/Rosetta/main/source/src/
export ROSETTA_DB=~/Rosetta/main/database/
export OUTPATH=~/git_repos/PDZ_ddG/results/
export INPATH=~/git_repos/PDZ_ddG/ancillary_files/
export SCRIPTS=~/git_repos/PDZ_ddG/scripts/


if [[ $prelim == '1' ]]
then
	$SCRIPTS'/'loop_pdbs.sh $INPATH'/input_pdbs/1g9o*.pdb' $INPATH'/input_pdbs/' "" 0 4 $SCRIPTS'/'score.sh $server
        $SCRIPTS'/'loop_pdbs.sh $INPATH'/input_pdbs/1g9o*_complex.pdb' $INPATH'/input_pdbs/' "" 0 4 $SCRIPTS'/'preprocess.sh $server

	exit
fi

if [[ $server == '0' ]]
then

	#performing pre_min1 step - only locally
	#this step is for chain A - just minimizing to generate constraint files
	$SCRIPTS'/'loop_pdbs.sh $INPATH'/input_pdbs/????.pdb' $OUTPATH'/'pre_min1'/' $INPATH'/'input_pdbs'/' 0 4 $SCRIPTS'/'pre_min.sh
        #this step is for complex - minimizing to get a pre_min structure
        $SCRIPTS'/'loop_pdbs.sh $INPATH'/input_pdbs/??????_complex.pdb' $OUTPATH'/'pre_min1'/' $INPATH'/'input_pdbs'/' 0 6 $SCRIPTS'/'pre_min.sh

	#performing flexpepdock prepack - only locally
	$SCRIPTS'/'loop_pdbs.sh $OUTPATH'/pre_min1/*_complex*.pdb' $OUTPATH'/'prepack'/' "" 4 6 $SCRIPTS'/'fpd_prepack.sh

        #performing a second pre_min (bb as well as sc) to prepare for ddg
        $SCRIPTS'/'loop_pdbs.sh $OUTPATH'/prepack/*.pdb' $OUTPATH'/'pre_min2'/' "" 4 6 $SCRIPTS'/'pre_min.sh

else
	#run ddg on pre_min pdbs
	$SCRIPTS'/'loop_pdbs.sh $OUTPATH'/pre_min2/*.pdb' $OUTPATH'/'ddg'/' "" 8 14 $SCRIPTS'/'ddg.sh $server 5 10

	#performing flexpepdock refine for 1g9o - only on server 
        #only one server because already partitioned the pdbs in the previous step
	$SCRIPTS'/'loop_pdbs.sh $OUTPATH'/ddg/*/*.pdb' $OUTPATH'/refine/' "" 8 6 $SCRIPTS'/'fpd_refine.sh 1 1 10

	$SCRIPTS'/'loop_pdbs.sh $OUTPATH'/refine/*/' $OUTPATH'/refine/' "" 0 6 $SCRIPTS'/'fpd_postprocess.sh 1 1 1 

        $SCRIPTS'/'loop_pdbs.sh $OUTPATH'/refine/*/' $OUTPATH'/ddg_csv/rosetta/' "" 0 4 $SCRIPTS'/'ddg_rmsd.sh $server 5 1

fi

