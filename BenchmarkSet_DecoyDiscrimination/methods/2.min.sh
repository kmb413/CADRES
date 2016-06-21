#!/bin/bash

path=$1
pdb=$2
outpath=$3
pdb_id=$4
scorefxn=talaris2014

strip_pdb="${pdb%.*}"

set_id=$(expr match "$path" '.*\(set.\)')

native_path=~/'CADRES/DecoyDiscrimination/Natives/natives.'$set_id'/'$pdb_id'.pdb'


mkdir -p $outpath
cd $outpath
	
grep -sq "reported success" $strip_pdb'_relax.log'
if [ $? -gt 0 ]; then
	~/Rosetta/main/source/bin/rosetta_scripts.static.linuxgccrelease -database ~/Rosetta/main/database -ex1 -ex2 -extrachi_cutoff 1 -use_input_sc -s $path'/'$pdb -parser:protocol ~/CADRES/DecoyDiscrimination/Rosetta/xml/min.xml -score:weights $scorefxn  -parser:script_vars SCORE=$scorefxn -in:file:native $native_path -nblist_autoupdate > $strip_pdb'_relax.log' 
fi
