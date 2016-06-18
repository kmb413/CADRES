#!/usr/bin/env python

'''python generate_rst7_parm7_files.py pdb_code_or_pdblist

Example
-------
    python generate_rst7_parm7_files.py 1vcc
        - strip H
        - generate new parm7 and rst7 files by tleap (will add H).

Requires
--------
ParmEd, tleap

Output
------
NoH*.rst7 and *.parm7 files
'''

import os
import sys
import parmed as pmd
from glob import glob, iglob
from subprocess import check_call

# current dir
from utils import temp_change_dir

##### Directories and Paths ##### TODO: CHANGE
BASE_DIR    =  "/scratch/kmb413/CADRES/BenchmarkSet_LoopModeling/methods"
NATIVES_DIR =  "{base_directory}/Natives".format( base_directory=BASE_DIR )
DECOY_DIR   =  "{base_directory}/loop_modeling_ngk_r57934/r57934/talaris2014/job_output".format( base_directory=BASE_DIR )
##########################

## Define tLeap parameters ##TODO: @Hai - you had source leaprc.protein.ff14SBonlysc. Is there a difference?
tleap_template = '''source leaprc.ff14SBonlysc 
m = loadpdb NoH_{pdbfile_root}.pdb
set default pbradii mbondi3
saveamberparm m {code}.parm7 NoH_{pdbfile_root}.rst7
quit
'''

def run_tleap(code, pdbfile_root, tleap_template):
    leap_fn = 'tleap.in' #.format(pdbfile_root)
    with open(leap_fn, 'w') as fh:
        cm = tleap_template.format(pdbfile_root=pdbfile_root, code=code)
        fh.write(cm)
    check_call('tleap -f {}'.format(leap_fn), shell=True)
    os.remove(leap_fn)

def main(pdblist, force=False):# pdb_pattern, force=False):
    for code in pdblist:
        try:
            os.mkdir('{base_directory}/amber_minimization/{PDB}'.format( base_directory=BASE_DIR, PDB=code ) )
        except OSError:
            pass
        
        with temp_change_dir('{base_directory}/amber_minimization/{PDB}'.format( base_directory=BASE_DIR, PDB=code ) ):
            print('processing {}'.format(code))
            print(os.getcwd())
            try:
                pdbfiles = glob('{decoy_directory}/{code}*.pdb'.format(decoy_directory=DECOY_DIR, code=code))
                for pdbfile in pdbfiles:
                    basename = os.path.basename(pdbfile)
                    try:
                        parm = pmd.load_file(pdbfile)
                        ok = True
                    except ValueError:
                        print('ParmEd failed: {}'.format(pdbfile))
                        ok = False
                    pdbfile_root = basename.replace('.pdb', '')
                    fn = 'NoH_' + basename
                    if os.path.exists(fn) and not force:
                        print('skip {}'.format(fn))
                    else:
                        if ok:
                            new_parm = parm[[index for index, atom in enumerate(
                                parm.atoms) if atom.atomic_number != 1]]
                            new_parm.save(fn, overwrite=True)
                            run_tleap(code, pdbfile_root, tleap_template)
            except TypeError:
                print('type error: ', code)
            except IndexError:
                print('index error: ', code)

if __name__ == '__main__':
    pdblist_ = sys.argv[1]
    #root = sys.argv[2]
    #PDB_PATTERN = root + '/{code}*.pdb'
    
    if os.path.isfile(pdblist_):
        with open(pdblist_) as fh:
            PDBLIST = fh.read().split()
    else:
        PDBLIST = pdblist_.split(',')
    
    main(pdblist=PDBLIST) #, pdb_pattern=PDB_PATTERN) 
