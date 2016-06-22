#!/bin/bash

pdb=$1
actual_fn=$2 
pdb_name=$3
pdb_final_outpath=$4 
cst_file=$5
server=$6

cd $pdb_final_outpath

mkdir -p $actual_fn
cd $actual_fn 

for i in {1..10}
do
	mkdir -p $i
        cd $i
        #technically doesn't check that log is complete so if may have stopped running in the middle should check this
	grep -sq "mutation label" $actual_fn'_ddg.log'
	if [ $? -gt 0 ];
	then
		$ROSETTA_BIN'/'ddg_monomer.static.linuxgccrelease -database $ROSETTA_DB -s $pdb -score:weights talaris2014_cst -out:prefix $server $cst_file -ex1 -ex2 -use_input_sc -ddg::mut_file $INPATH'/'mut_file'/'$pdb_name'.mut_file'  -ddg:weight_file soft_rep_design -ddg:minimization_scorefunction talaris2014_cst -fa_max_dis 9.0 -ddg::iterations 5 -ddg::dump_pdbs true -ddg::local_opt_only false -ddg::min_cst true -ddg::suppress_checkpointing true -in::file::fullatom -ddg::mean false -ddg::min true -ddg::sc_min_only false -ddg::ramp_repulsive true > $actual_fn'_ddg.log' &
	fi
	cd ../
done

wait

rm -f ddg_data.txt

for i in {1..10}
do
	cd $i
	awk -v i=$i ' $0 ~/round .* mutate/ {print i,$3,$5,$6}' $actual_fn'_ddg.log' >> ../ddg_data.txt
	awk -v i=$i ' $0 ~/score before mutation/ {print i, $2, "wt", $7}' $actual_fn'_ddg.log' >> ../ddg_data.txt 
	cd ../
done

uniq_seq=( $(awk '{print $3}' ddg_data.txt | sort | uniq) )

for s in "${uniq_seq[@]}"
do
	#filedata=$(awk -v s=$s ' "s" == $3 {print $1,$2,$4}' ddg_data.txt)
	file_data=( $(awk -v s=$s '$3 == s {print $1,$2,$4}' ddg_data.txt | sort -nk 3 | head -n 3 | awk -v s=$s '{ if (s == "wt"){print $1"/repacked_wt_round_"$2".pdb"} else {print $1"/mut_"s"_round_"$2".pdb"}}') )

	for i in "${file_data[@]}" 
	do
		destination="${i/\//_}"
		cp $i $destination
	done	
done
