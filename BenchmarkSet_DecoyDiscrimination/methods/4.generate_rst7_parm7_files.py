#!/usr/bin/env python

'''python generate_rst7_parm7_files.py pdb_code

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

_PDBLIST = sys.argv[1]
SCRIPT_PATH = './scripts'
root = '.'
PDB_PATTERN = 'empty*.pdb'

if os.path.isfile(_PDBLIST):
    with open(_PDBLIST) as fh:
        PDBLIST = fh.read().split()
else:
    PDBLIST = _PDBLIST.split(',')

sys.path.append(SCRIPT_PATH)

from submit_elf1 import temp_change_dir

tleap_template = '''logFile log.{pdbfile_root}
source leaprc.protein.ff14SBonlysc
m = loadpdb NoH_{pdbfile_root}.pdb
set default pbradii mbondi3
saveamberparm m {pdbfile_root}.parm7 NoH_{pdbfile_root}.rst7
quit
'''

def run_tleap(code, pdbfile_root, tleap_template):
    leap_fn = 'tleap.{}.in'.format(pdbfile_root)
    with open(leap_fn, 'w') as fh:
        cm = tleap_template.format(pdbfile_root=pdbfile_root)
        fh.write(cm)
    os.system('tleap -f {}'.format(leap_fn))
    os.remove(leap_fn)
    os.remove('log.{}'.format(pdbfile_root))

def main():
    for code in PDBLIST:
        with temp_change_dir(code):
            try:
                pdbfiles = glob(PDB_PATTERN)
                for pdbfile in pdbfiles:
                    parm = pmd.load_file(pdbfile)
                    pdbfile_root = pdbfile.replace('.pdb', '')
                    fn = 'NoH_' + pdbfile
                    new_parm = parm[[index for index, atom in enumerate(
                        parm.atoms) if atom.atomic_number != 1]]
                    new_parm.save(fn, overwrite=True)
                    run_tleap(code, pdbfile_root, tleap_template)
            except TypeError:
                print('type error: ', code)
            except IndexError:
                print('index error: ', code)

if __name__ == '__main__':
    main()
