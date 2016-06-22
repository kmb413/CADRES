#!/bin/bash

ls *.pdb > list
~/Rosetta/main/source/bin/FlexPepDocking.default.linuxgccrelease -database ~/Rosetta/main/database/ -l list -flexpep_score_only -score:weights ~/Rosetta/main/database/scoring/weights/talaris2014_cst.wts
awk '{ sum += $6+$38; n++ } END { if (n > 0) print sum / n; }' score.sc > Average_I_score.txt
/home/emd182/Rosetta/main/source/bin/rosetta_scripts.linuxgccrelease -l list -use_input_sc -database /home/emd182/Rosetta/main/database/ -parser:protocol Interfaceselector.xml -parser:script_vars chain1=A chain2=B -overwrite | grep "pymol" >> list_of_neighbors.txt
./get_average_amber_energy.pl res.csv list_of_neighbors.txt
