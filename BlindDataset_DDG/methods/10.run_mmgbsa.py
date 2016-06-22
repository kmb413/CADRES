#!/usr/bin/env python

import os
import shutil
from glob import iglob
import json
from subprocess import check_call
import parmed as pmd
import pandas as pd

MMGBSA_INPUT = """Input file for running MMGBSA with GBneck2 model
&general
   endframe=50, verbose=2,
   keep_files=1,
   use_sander=1,
/
&gb
  igb=8,
/
"""

def check_amberhome():
    amberhome = os.getenv('AMBERHOME')

    if amberhome is None:
        raise OSError("must set AMBERHOME")

def write_mmgbsa_input():
    with open("mmgbsa.in", 'w') as fh:
        fh.write(MMGBSA_INPUT)

def parse_ligand_mask():
    root = '../' 
    first_pdb = next(iglob(root + 'No*.pdb'))
    parm = pmd.load_file(first_pdb)
    
    final_res = len(parm.residues) + 1
    first_res_ligand = None
    
    for index, res in enumerate(parm.residues):
        if res.chain == 'B':
            first_res_ligand = index + 1
            break
    
    strip_ligand_mask = ':' + str(first_res_ligand) + '-' + str(final_res)
    strip_receptor_mask = ':1-' + str(first_res_ligand-1)
    
    print('ligand_mask = ', strip_ligand_mask, 'receptor_mask = ', strip_receptor_mask)
    return strip_ligand_mask, strip_receptor_mask

def run_mmgbsa(prmtop='../prmtop', rst7_dir='../no_restraint_new_protocol/'):
    strip_ligand_mask, strip_receptor_mask = parse_ligand_mask()
    try:
        os.remove('receptor.parm7')
        os.remove('peptide.parm7')
    except OSError:
        pass

    check_call("$AMBERHOME/bin/ante-MMPBSA.py -p ../prmtop -s '{}' -c receptor.parm7".format(strip_ligand_mask), shell=True)
    check_call("$AMBERHOME/bin/ante-MMPBSA.py -p ../prmtop -s '{}' -c peptide.parm7".format(strip_receptor_mask), shell=True)
    
    cm = "$AMBERHOME/bin/MMPBSA.py -i mmgbsa.in -cp {prmtop} -y {rst7_dir}/min*rst7 -rp ./receptor.parm7 -lp peptide.parm7 -eo eout.csv".format(
            prmtop=prmtop,
            rst7_dir=rst7_dir)
    check_call(cm, shell=True)
    
    check_call("grep 'gas,DELTA G solv,DELTA TOTAL' eout.csv -A50 > temp2.csv", shell=True)

def get_filelist():
    filelist = None
    with open('_MMPBSA_info') as fh:
        for line in fh:
            if line.startswith("FILES.mdcrd"):
                filelist = eval(line.split('=')[-1])
    return filelist

def write_ddg_csv():
    filelist = get_filelist()
    x = pd.read_csv("temp2.csv")['DELTA TOTAL']
    out = "\n".join(fn + ',' + str(ddg) for (fn, ddg) in zip(filelist, x))
    
    with open('ddG.csv', 'w') as fh:
        fh.write(out)

def clean(mmgbsa_file=False):
    try:
        os.mkdir('logs')
    except OSError:
        pass
    src = './logs'

    for fn in iglob('_*MM*'):
        check_call('mv {} {}/'.format(fn, src), shell=True)

    check_call("mv peptide.parm7 {}/".format(src), shell=True)
    check_call("mv receptor.parm7 {}/".format(src), shell=True)
    check_call("mv temp2.csv {}/".format(src), shell=True)
    check_call("mv eout.csv {}/".format(src), shell=True)

def main():
    check_amberhome()
    write_mmgbsa_input()
    run_mmgbsa(rst7_dir='../')
    write_ddg_csv()
    clean(mmgbsa_file=True)

if __name__ == '__main__':
    main()
