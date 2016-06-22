#!/bin/bash

regex_files=$1 #quote wildcards in single quotes
pdb_outpath=$2
cst_outpath=$3 #if you don't want to generate cst files and you want to use pregenerated cst files, leave this blank (i.e. "")
pdb_start=$4
pdb_end=$5
script=$6
server=$7
n_servers=$8
n_cores_per_script=$9

input_pdb=($regex_files)

mkdir -p $pdb_outpath

if [[ $input_pdb =~ "*" ]]
then
	echo "No filenames found"
	exit
fi

#determines begin and end indices based on how many files there are and how many servers there are
n_files=${#input_pdb[@]}

n_files_in_group=$(( $n_files / $n_servers + 1 ))
begin_index=$(( $n_files_in_group * ($server-1) ))

echo "Looping"
echo "Filenames are ${input_pdb[@]:$begin_index:$n_files_in_group}"

#sets counters
counter=0

n_cores=40

#n_cores_per_script must be a factor of n_cores TODO: output warning if not
if [ ! -z ${n_cores_per_script} ];
then
        n_cores=$(( $n_cores / $n_cores_per_script ))
fi

for pdb in "${input_pdb[@]:$begin_index:$n_files_in_group}";
do
        counter=$(( $counter + 1 ))

	echo "Processing $pdb"

	actual_fn=$(basename $pdb)
	actual_fn="${actual_fn%.*}"

	echo "Actual filename is $actual_fn"

	pdb_name=${actual_fn:$pdb_start:$pdb_end}
        cst_pdb_name=${actual_fn:$pdb_start:4}

	dir_name=$(basename $(dirname $pdb))
	
        #check if this is part of an NMR ensemble
        if [[ ${actual_fn:$pdb_start} =~ [0-9a-z]{4}[0-9]{2}_00[0-9]{2} || $dir_name =~ [0-9a-z]{4}[0-9]{2}_00[0-9]{2} ]]
	then
		pdb_end_curr=$(( pdb_end + 5 ))
		pdb_name=${actual_fn:$pdb_start:$pdb_end_curr}
		model_n_start=$(( $pdb_start + 7 ))
		cst_pdb_name=${actual_fn:$pdb_start:4}_${actual_fn:$model_n_start:4}
		nmr=1
	else
		nmr=0
	fi

        if [[ $cst_outpath == "" ]]
        then

	        cst_fn=$INPATH'/input_pdbs/'$cst_pdb_name'.cst'

		echo "Constraint filename is $cst_fn"

		cst_file="-cst_fa_file $cst_fn"
		echo "No constraint path was provided. Will use pregenerated constraint file and will not generate new one"
                echo "Constraint filename is $cst_file"
	else
		cst_file=$cst_outpath
	fi

	#pdb name is provided so that ddg can find mutfile
	#nmr is provided for fpd_refine
	$script $pdb $actual_fn $pdb_name $pdb_outpath "$cst_file" $server $nmr &

        if (( $counter % $n_cores == 0 ));
             then
             wait
        fi

done
wait
