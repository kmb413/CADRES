#!/bin/bash

if [ "$1" == "-h" ]; then
  echo "Usage: <inputpath> <filepattern> <outpath> <level_pdb_id> <script> <n_servers> <this_server> <scorefxn> <n_cores_per_script>"
  echo "Sample: /home/arubenstein/CADRES/DecoyDiscrimination/decoys.set1.init/1vkk/ *.pdb /home/arubenstein/CADRES/DecoyDiscrimination/Rosetta/relax/decoys.set1/SCORE/1vkk/ 1 relax.sh 1 1 talaris2014 1"
  exit 0
fi

#Possible Usage Scenarios:
#1. run on all files matching a filepattern in a given directory - inner_dir_name is the name of the file without its extension.
#   a. specific pdb - decoys.set1.init/1vkk/ *.pdb
#   b. all pdbs - decoys.set1.init/ *.out
#2. run on all files within all directories in a given directory - inner_dir_name is the name of each directory
#   a. all pdbs - relax/decoys.set1.init/ "none"

inputpath=$1
filepattern=$2
outpath=$3
level_pdb_id=$4 #level of pdb_id in inputpath as NF-x. e.g. .../decoys.set1.init/ "none" level_pdb_id = 0, .../min/decoys.set1.init/talaris2013/1vkk/ "none" level_pdb_id = 1 
script=$5
n_servers=$6
this_server=$7
scorefxn=$8
n_cores_per_script=$9

cd $inputpath

#search for appropriate files based on filepattern
#if filepattern is none searches for directories instead

if [ "none" = "$filepattern" ];
then
	second_loop=1
	ls -l | grep '^d' | awk '{print $9}' > files_list.txt
else
	second_loop=0
	ls ''$filepattern'' > files_list.txt
fi

#determines begin and end indices based on how many files there are and how many servers there are
n_files=$( wc -l files_list.txt | awk '{print $1}')

n_files_in_group=$(( $n_files / $n_servers + 1 ))
end_index=$(( $n_files_in_group * $this_server ))
this_server=$(( $this_server - 1 ))
begin_index=$(( $n_files_in_group * $this_server))

#sets counters
counter=0

filecounter=0

n_cores=50

#n_cores_per_script must be a factor of n_cores TODO: output warning if not
if [ -z ${n_cores_per_script+x} ];
then
	n_cores=$(( $n_cores / $n_cores_per_script ))
fi	

#loops thru file of filenames or dir names
while read item
do
	
        filecounter=$(( $filecounter + 1 ))

	#if filecounter is between beginning and end indices
        if [ $filecounter -gt $begin_index ] && [ $filecounter -le $end_index ];
        then

		#set inner_dir_name
                inner_dir_name="${item%%.*}"

	        final_outpath=$outpath'/'$inner_dir_name
		final_outpath=${final_outpath/SCORE/$scorefxn}
		if [[ $second_loop -eq "1" ]]
		then
			final_inpath=$inputpath'/'$item
		else
			final_inpath=$inputpath
		fi

		final_inpath=${final_inpath%/}
		pdb_id=$(awk -F/* -v i=$level_pdb_id '{print $(NF-i)}' <<<"${final_inpath}" )
		
		#if looping thru dirs then loop thru files inside
		if [[ $second_loop -eq "1" ]]
		then
			cd $final_inpath
			for pdb in $(ls *.pdb)
			do
			     counter=$((counter+1))
			     strip_pdb="${pdb%.*}"
			     eval nohup "/home/arubenstein/CADRES/DecoyDiscrimination/Rosetta/scripts/$script" $final_inpath $pdb $final_outpath'/'$strip_pdb $pdb_id $scorefxn &
			     if (( $counter % $n_cores == 0 ));
				then
				wait
			     fi
			done
                	cd $inputpath
		else
	
		     counter=$((counter+1))
		     eval nohup "/home/arubenstein/CADRES/DecoyDiscrimination/Rosetta/scripts/$script" $final_inpath $item $final_outpath $pdb_id $scorefxn &
		     if (( $counter % $n_cores == 0 )); 
			then
			wait
		     fi
		fi
	fi
done < files_list.txt

wait

filecounter=0

#postprocessing
while read item
do

    filecounter=$(( $filecounter + 1 ))

    #if filecounter is between beginning and end indices
    if [ $filecounter -gt $begin_index ] && [ $filecounter -le $end_index ];
    then

	    #set inner_dir_name
	    inner_dir_name="${item%%.*}"

	    final_outpath=${outpath/SCORE/$scorefxn}
	    if [[ $second_loop -eq "1" ]]
	    then
		inner_dir_name="${item%%.*}"
		final_outpath=$final_outpath'/'$inner_dir_name
	    fi

	    cd $final_outpath
	    cat */score.sc | awk ' (NR == 1 || NR == 2) || ($1 != "SEQUENCE:" && $2 ~ /[0-9]/) {print}' > final_score.sc

    fi

done < files_list.txt


cd $inputpath
rm files_list.txt
