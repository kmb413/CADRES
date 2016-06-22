#!/bin/bash

pdb=$1
actual_fn=$2 
pdb_name=$3
pdb_final_outpath=$4
cst_param=$5

#set cst parameter appropriately
if [[ $cst_param =~ "cst_fa_file" ]]
then
	cst_file=$cst_param
	cst_outpath=""
else
	cst_file=""
	cst_outpath=$cst_param
fi

cd $pdb_final_outpath
        
#kludgy workaround because minimize_with_cst requires a list, not a file
echo $pdb > $actual_fn'.list'

#set fa_max_dis to 9 (even though may not be the best setting) because doesn't appear to matter much for now
$ROSETTA_BIN'/'minimize_with_cst.linuxgccrelease -in:file:l $actual_fn'.list' -in:file:fullatom -fa_max_dis 9.0 -database $ROSETTA_DB -ddg::harmonic_ca_tether 0.5 $cst_file -score:weights talaris2014_cst -ddg::constraint_weight 1.0 -ddg::out_pdb_prefix 'min' -ddg::sc_min_only false > $actual_fn'.log'

mv 'min.'$actual_fn'_0001.pdb' 'min_'$actual_fn'_0001.pdb'

#remove temp files
rm $actual_fn'.list'

if [[ $cst_outpath != "" ]]
then
	
	#convert log to cst file
	$ROSETTA_SRC'/'apps/public/ddg/convert_to_cst_file.sh $actual_fn'.log' > $cst_outpath'/'$actual_fn'.cst'
	echo "Converted log to cst file $cst_outpath'/'$actual_fn'.cst'"
fi
echo "Successfully completed pre_min for $pdb"

