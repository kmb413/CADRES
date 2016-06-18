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

Instructions
============

### To run the method on all PDBs in the short-loop set,

#### First, unzip the loop_modeling_ngk_r57934.7z archive, which contains all the decoy structures:

```bash
7za loop_modeling_ngk_r57934.7z
```

- Note: There exists an extracted loop_modeling_ngk_r57934 folder, but this only contains decoy structures for
the 1oyc example.

#### Then, minimize the decoy structures using Rosetta:

```bash
python 1.Rosetta_Minimize.py pdblist

# pdblist is a file containing a list of all 45 short-loop PDB IDs.
```

- **Description**  
    - This script will make a `/rosetta_minimization directory` in which it will also make
sub-directories for each of the 45 PDB IDs. In each sub-directory, it will write several
minimization bash scripts that have a slurm-style queueing system header and the
minimization command. The minimization scripts will be automatically submitted to the queue
unless auto_submit is explicitly turned off:

        ```bash
        python 1.Rosetta_Minimize.py pdblist 0
        ```
        - If you use this flag, you must cd into each directory and bash each min*.sh script.

    - The minimization is carried out via RosettaScripts, where the loop region is minimized with BB and SC movements on. The rest of the protein is left fixed.

    - Flags: 
        - -score:weights talaris2014 
        - -ex1 
        - -ex2 
        - -extrachi_cutoff 1 
        - -use_input_sc 
        - -nblist_autoupdate

- **Expected Output**
    - A `/rosetta_minimization/` directory
        - `/rosetta_minimization/{PDB_Code}` directories
            - `min*.sh` scripts.
            - `{PDB_code}.*.list` files, which are lists containing the filepaths to 100 or less decoy structures.

            - After the min*.sh scripts have run, 
                - `{decoy_pdb}_0001.pdb` files
                - `score.*.sc files`, one for each of the `{PDB_code}.*.list` files.

#### Concurrently, minimize the decoy structures using Amber:

```bash
python 2.Amber_MinimizationSetUp pdblist
python 3.Amber_GenerateRST7andParm7.py pdblist
for pdb in `cat pdblist`
    do
        cd amber_minimization/$pdb
        python ../../4.Amber_RunMinimization.py -p $pdb.parm7 \
            -O -c "NoH*.rst7" -i min.in
        cd ../../
    done
```
- **Description**
    - The script `2.Amber_MinimizationSetUp` creates the `/amber_minimization` directory in which it also creates
    sub-directories for each of the 45 PDB IDs. In each of these sub-directories, it will also write a min.in file
    that specifies the minimization parameters for Amber minimization.
    - The script `3.Amber_GenerateRST7andParm7.py` creates a list of decoy structures from the unarchived folder under a 
    single {PDB_Code}, removes all Hydrogen atoms, inputs these structures into tLeap, and generates coordinates files (.rst7) and a topology file (.parm7) for each of the decoy structures. 
    - The script `4.Amber_RunMinimization.py` runs the Amber minimization command on all .rst7 files in each {PDB_Code} directory, where the .parm7 file is given under the `-p` flag, the .rst7 files are given under the `-c` flag, and the minimization parameters script `min.in` is given under the `-i` flag.
        
         - Minimizations were performed using 14SBonlysc force field and GBNeck2 implicit solvent model. XMIN method is used with max cycles of 1000. Minimization will be stopped if the root-mean-square of the Cartesian elements of the gradients is less than 0.01 kcal/mol. The heavy atoms of non-loop region were restrained with restraint force constant of 10.0 (kcal/mol-Å^2)
         - All minimization and energy evaluations were performed with `sander` and its Python interface `pysander` program in development version of [AmberTools16](http://ambermd.org/AmberTools16-get.html)

- **Expected Output**
    - An `/amber_minimization` directory  
        - `/amber_minimization/{PDB_Code}` directories  
            - `min.in` file  
            - `NoH_{decoy_structure}.rst7` files  
            - `{PDB_Code}.parm7` file  
                
            - After the minimizations have run,
                - `min_NoH_{decoy_structure}.rst7` files

### Score the Amber-minimized structures:

```bash
python make_energy_bashscripts.py pdblist
for SCRIPT in `ls GetScores*.sh`; do sbatch $SCRIPT ; done
```

- **Description**
    - The wrapper script `make_energy_bashscripts.py` makes slurm-style queueing system bash scripts that run the `5.Amber_GetEnergies.py` script on all {PDB_Codes} in the pdblist file.
    - The `for-loop` sends all of the bash scripts to the queueing system.
    - The script `5.Amber_GetEnergies.py` evaluates the Amber energy of the native structure as well as the decoy structures for each `/amber_minimization/{PDB_Code}/min*.rst7` file, and calculates the CA-RMSD of each decoy structure with respect to the native structure without superimposition. It also calculates the CA-RMSD of the the loop-region only with superimposition.

- **Expected Output**
    - Several `GetScores_*.sh` scripts
    - After the energy calculation scripts have run,
        - `/amber_minimization/{PDB_Code}/{PDB_Code}_amber.sc` files
    
    

#### Choose the 'best' scoring decoy structures using both Amber and Rosetta scores:
