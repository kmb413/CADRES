#!/usr/bin/env python

'''python generate_rst7_parm7_files.py pdblist

What does this do? 

    - strip H
    - generate new parm7 and rst7 files by tleap (will add H).

Requires
--------
ParmEd, tleap

Output
------
NoH*.rst7 and prmtop files in each folder
'''

import os
import sys
import parmed as pmd
from glob import glob, iglob
from subprocess import check_call

# current folder
from utils import temp_change_dir

TLEAP_TEMPLATE = '''source leaprc.protein.ff14SBonlysc
m = loadpdb NoH_{pdbfile_root}.pdb
set default pbradii mbondi3
saveamberparm m prmtop NoH_{pdbfile_root}.rst7
quit
'''

def run_tleap(code, pdbfile_root, TLEAP_TEMPLATE):
    print("running tleap")
    leap_fn = 'tleap.{}.in'.format(pdbfile_root)
    with open(leap_fn, 'w') as fh:
        cm = TLEAP_TEMPLATE.format(pdbfile_root=pdbfile_root, code=code)
        fh.write(cm)
    check_call('tleap -f {}'.format(leap_fn), shell=True)
    os.remove(leap_fn)

def main(pdblist, pdb_pattern, force=False):
    for code in pdblist:
        try:
            print("trying to make {} folder".format(code))
            os.mkdir(code)
        except OSError:
            pass
        with temp_change_dir(code):
            print('processing {}'.format(code))
            print(os.getcwd())
            try:
                pdbfiles = glob(PDB_PATTERN.format(code=code))
                assert len(pdbfiles) > 0, "can not find any pdb file"
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
                            run_tleap(code, pdbfile_root, TLEAP_TEMPLATE)
            except TypeError:
                print('type error: ', code)
            except IndexError:
                print('index error: ', code)

if __name__ == '__main__':
    """python generate_rst7_parm7_files.py code root_dir
    """
    pdblist_ = sys.argv[1]
    pdb_root_dir = sys.argv[2]
    PDB_PATTERN = pdb_root_dir + '/{code}/*.pdb'

    if os.path.isfile(pdblist_):
        with open(pdblist_) as fh:
            PDBLIST = fh.read().split()
    else:
        PDBLIST = pdblist_.split(',')
    
    main(pdblist=PDBLIST, pdb_pattern=PDB_PATTERN) 
