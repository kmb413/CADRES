#!/bin/bash

path=$1
filename=$2
outpath=$3
pdb_id=$4

mkdir -p $outpath
cd $outpath
	
/home/arubenstein/CADRES/DecoyDiscrimination/extract_pdbs.static.linuxgccrelease -database /home/arubenstein/CADRES/DecoyDiscrimination/Rosetta_Database/ -in:file:silent $path'/'$filename > extract_pdbs.log
