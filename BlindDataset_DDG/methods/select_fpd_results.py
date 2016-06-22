#!/usr/bin/env python

import os
import argparse
from customIO import scorefileparse
from shutil import copyfile
from math import ceil

def main(path_prefix):
    scores_dict = scorefileparse.read_vals(path_prefix+"/final_score.sc", "rosetta", rmsd="rmsALL", trim=False)

    sorted_energies = sorted(scorefileparse.get_energies(scores_dict))
    bottom_20_pct = sorted_energies[0:len(sorted_energies)/5]
    
    scores_bottom_20 = dict(( key, (e, r)) for key, (e, r) in scores_dict.items() if e in bottom_20_pct )
    #sorted_rmsd = sorted(scorefileparse.get_rmsd(scores_bottom_20)) 
    
    sorted_keys_by_r = sorted(scores_bottom_20.keys(), key=lambda x: scores_bottom_20[x][1])

    length = float(len(sorted_keys_by_r))
    sel_pdbs = [ sorted_keys_by_r[int(ceil(i * length / 50))] for i in range(50) ]

    #to see how long directory names are (dependent on NMR or xtal)
    test_dir = next(os.walk(path_prefix + "/"))[1][0]
    length_dir = len(test_dir.split("_"))
    
    for pdb in sel_pdbs:
	parent_dir = '_'.join(pdb.split("_")[0:length_dir])
	src = "{0}/{1}/{2}.pdb".format(path_prefix,parent_dir,pdb)
        dst = "{0}/{1}.pdb".format(path_prefix,pdb)
        copyfile(src, dst)        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--path_prefix', help="path of final_score.sc")

    args = parser.parse_args()

    main(args.path_prefix) 
