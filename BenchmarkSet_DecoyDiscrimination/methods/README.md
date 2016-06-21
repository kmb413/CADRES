Requirements
============
- 7za
- python2.7
    - Modules:
        - pandas
        - glob
        - subprocess
        - MPI
        - argparse
        - getopt
- RosettaScripts
- [AmberTools16](http://ambermd.org/AmberTools16-get.html)

Files Included
==============

***Rosetta Run***
- **1.extract.sh** Extract pdb files from silent files for Rosetta run
- **2.min.sh** Minimize and score decoys for rmsd 
    - **min.xml** helper script for above

***Amber Run***
- **3.pdbgen_from_rosetta.py** Extract pdb files from silent files for Amber run
- **4.generate_rst7_parm7_files.py** Generate topology and resart files for Amber minimization
- **5.run_min.py** Run minimization
    - **min.in** helper script for above
- **6.eamber_single.py** Get AMBER potential energies

***Wrapper/helper scripts***
- **utils.py** Used in Amber run
- **submit_elf1.py** Wrapper script for Amber run
- **loop_pdbs.sh** Wrapper script for Rosetta run

Instructions
============

### To run the method on all decoys in silent files for a given set (e.g. decoys.set1 or decoys.set2)

#### 1. place the silent files in $BASEDIR/input/decoys.set<set_number>
#### 2. extract pdbs from the silent files
- Script for one silent file
```bash
1.extract.sh $BASEDIR/input/decoys.set1/ 1a32.1000.out $BASEDIR/input/decoys.set1/1a32/ 1a32
```
- Wrapper script to extract all silent files when run on one server
```bash
loop_pdbs.sh $BASEDIR/input/decoys.set1/ "*.out" $BASEDIR/input/decoys.set1/ 0 1.extract.sh 1 1 talaris2014 1
```
#### 3. run Rosetta minimization
- Script for one decoy
```bash
2.min.sh $BASEDIR/input/decoys.set1/1a32/ empty_tag_11229_0001.pdb $BASEDIR/output/decoys.set1/1a32/ 1a32 
```
- Wrapper script to minimize all decoys in given set when run on one server
```bash
loop_pdbs.sh $BASEDIR/input/decoys.set1/ "none" $BASEDIR/output/decoys.set1/ 0 2.min.sh 1 1 talaris2014 1
```

#### 4. extract pdbs from the silent files for AMBER minimization (unnecessary if Step 1 has already been done) 
- Generate all pdb files for AMBER with given pdb code (e.g. `1a32`)
```bash
python 3.pdbgen_from_rosetta.py 1a32
# Notes: I only include a single structure in `1a32` for demo
```
#### 5. generate amber files
- Generates coordinates files (.rst7) and a topology file (.parm7) for a given pdb code
```bash
python 4.generate_rst7_parm7_files.py 1a32
```
#### 6. run Amber minimization
- Run minimization
```bash
cd 1a32/
python ../scripts/5.run_min.py -p empty_tag_11229_0001.parm7 -c "NoH*.rst7" -i ../input/min.in

# minimized coordinate filename: min*rst7
```
#### 7. get AMBER potential energy 
- Get AMBER potential energy for a given pdb code
```bash
# make sure to adjust script to your need
python scripts/7.eamber_single.py

# Expectation: AMBER potential energy for one of snapshots
# ('1a32/min_NoH_empty_tag_11229_0001.rst7', -3661.805075801537)
```

Methods
-------
- Minimization were performed using 14SBonlysc force field and GBNeck2 implicit solvent model.
XMIN method is used with max cycles of 1000. Minimization will be stopped if the root-mean-square
of the Cartesian elements of the gradients is less than 0.01 kcal/mol.

- The potential energies of final snapshots were then evaluated by `sander` program via its Python interface (`pysander`)

All minimization and energy evaluations were performed with the development version of [AmberTools16](
http://ambermd.org/AmberTools16-get.html)
~                                           
