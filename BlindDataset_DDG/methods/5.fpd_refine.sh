#!/bin/bash

pdb=$1
actual_fn=$2 
pdb_name=$3
pdb_final_outpath=$4
cst_file=$5
server=$6
nmr=$7

dir_prefix=$(basename $(dirname $pdb))

if [[ $nmr -eq 1 ]];
then
	model_num=${dir_prefix:15:4}
	nstruct=1
else
	nstruct=20
fi	

dir_prefix=${dir_prefix:8:6}

dir_suffix=$(echo $actual_fn | awk -F_ '{print $3}')

o_dir_prefix=${dir_prefix:0:4}
log_name=$o_dir_prefix'_'$dir_suffix'_refine.log'

old_actual_fn=$actual_fn
actual_fn=$dir_prefix'_'$dir_suffix

cd $pdb_final_outpath
mkdir -p $actual_fn
cd $actual_fn

cst_file=""

for i in {1..10}
do
	ddg_iter=$(echo $old_actual_fn | awk -F_ '{print $1}')
	ddg_round=$(echo $old_actual_fn | awk -F_ '{print $5}')
        prefix=$ddg_iter'_'$ddg_round'_'$i

        if [[ $nmr -eq 1 ]];
	then
		prefix=$model_num'_'$prefix
	fi

	mkdir -p $prefix

        cd $prefix
	grep -sq "reported success" $log_name
	if [ $? -gt 0 ];
	then
		nohup nice $ROSETTA_BIN'/'FlexPepDocking.static.linuxgccrelease -database $ROSETTA_DB -s $pdb -score:weights talaris2014_cst -out:prefix $prefix'_' $cst_file -pep_refine -nstruct $nstruct -ex1 -ex2 -use_input_sc > $log_name &
	fi
	cd ../
done

wait

cat */*score.sc | awk ' (NR == 1 || NR == 2) || ($1 != "SEQUENCE:" && $2 ~ /[0-9]/) {print}' > final_score.sc
