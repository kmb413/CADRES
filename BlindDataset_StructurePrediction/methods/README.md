Requirements
============
- python2.7
    - Modules:
        - glob
        - MPI
- RosettaScripts
- [AmberTools16](http://ambermd.org/AmberTools16-get.html)

Files Included
==============

***Rosetta Run***
- **1.FastRelax_Initial.sh** Adds coordinate constraints to crystal structure and fastrelaxes it
    - **xmls/fastrelax.xml** helper script for above 
- **2.Mutate_to_all_ALA.sh** Mutate all non-loop residues to ALA and loop residues to designed identities
    - **xmls/make_allala.xml** helper script for above
- **3.ThreadSeq_and_RemodelLoop.py** Remodels the loop region and threads mutated sequence onto decoy structure
    - **xmls/mutate_kicloop.xml** helper script for above
- **4.FastRelax_LoopandMutantsPlusNeighbs.py** FastRelax loop, mutations, and neighbors of the region
    - **xmls/fastrelax_kicloop.xml** helper script for above
***Amber Run***
- **5.AmberMinimize.py** Minimize the decoys in Amber
    - **min_norestraint.in** helper script for above
- **6.GetAmberEnergies.py** Evaluate Amber energies 

Instructions
============

### To predict the structure of the mutant 1igs,

#### 1. First, FastRelax the crystal structure of 1igs:

```bash
# Before running script, change the ROS_EXE variable to your executables path, ROS_DB to your database path, and BASE_DIR to the dir above the methods folder.

bash 1.FastRelax_Initial.sh
```

- Note: The lowest-energy fastrelaxed structure has been moved to this directory (`1igs_0001_0037.pdb`).

- **Description**
    - Adds coordinate constraints to the crystal structure, then fastrelaxes (repeats=5) the structure with an nstruct of 50.
    
- **Expected Output**
    - A `../work/fastrelax_init/` directory
        - 50 `1igs_0001_00*.pdb` files
        - A `score_fastrelax_initial.sc` file.

#### 2. Then, mutate all non-loop residues to ALA, and thread the mutated sequence on the loop region:

```bash
# Before running script, change ROS_EXE to your executables path, ROS_DB to your database path, and BASE_DIR to the dir above the methods folder.

bash 2.Mutate_to_all_ALA.sh
```

- **Description**  
    - This script runs the `make_allala.xml` protocol on the lowest-energy fastrelaxed crystal structure.
    - The `make_allala.xml` protocl uses the SimpleThreadingMover to mutate all non-loop residues to alanines and all loop residues to the designed identities, such that remodeling of the loop region will not be hindered by side-chain clashes.

- **Expected Output**
    - A `../work/make_allala/` directory
        - A `1igs_0001_????_0001.pdb` file.
        - A `allala.sc` file.

#### 3. Remodel the loop region and then thread the entire mutated sequence onto the decoy structure:

```bash
# Before running script, change the ROS_EXE variable to your executables path, ROS_DB to your database path, and BASE_DIR to the dir above the methods folder.

python 3.ThreadSeq_and_RemodelLoop.py
```

- **Description**  
    - This script makes a directory in which it write 40 bash scripts that each run the `mutate_kicloop.xml` on the 1igs_0001_0037_0001.pdb input file 25 times.
    - The `mutate_kicloop.xml` script remodels the mutated loop region using the LoopRemodel mover, and then threads the entire mutated sequence onto the decoy structure.

- **Expected Output**
    - A `../work/RemodelLoop_ThreadSeq/` directory.
        - 40 bash scripts that run the xml protocol a total of 1000 times on the input file.
        - After the scripts have run, 
            - 1000 decoy structures, each with slightly different loop structures and full mutated sequences.

#### 4. FastRelax the loop region and mutated residues, along with their neighboring residues:

```bash
# Before running script, change ROS_EXE to your executables path, ROS_DB to your database path, and BASE_DIR to the dir above the methods folder.

python 4.FastRelax_LoopandMutantsPlusNeighbs.py
```

- **Description**  
    - This script makes a directory in which it writes bash scripts for all 1000 decoys in the `3.RemodelLoop_ThreadSeq/` directory.
    - The `fastrelax_kicloop.xml` protocol uses the FastRelax mover with repeats=5 and task_operations that turn off design for residues that are not part of the loop region, a mutated residue, or a neighbor residues within 8A of the loop or mutated residues.

- **Expected Output**
    - A `../work/FastRelax_LoopandMutantsPlusNeighbs/` directory
        - 40 bash scripts that run the xml protocol on each of the 1000 structures in the `3.RemodelLoop_ThreadSeq/` directory.
        - After the scripts have run,
            - 5000 decoy structures.
            - 40 `fastrelaxed_*.sc` files.

#### 5. Minimize the decoys in Amber:

```bash
# Before running script, change BASE_DIR to the dir above the methods folder and AMBER_SOURCE to the location of your AmberTool16 amber.sh file.

python 5.AmberMinimize.py
```

- **Description**  
    - This script makes a directory in which it writes bash scripts to run Amber minimization.
    - Each bash script removes the Hydrogen atoms from the decoys in the `4.FastRelax_LoopandMutantsPlusNeighbs/` directory, converts them to `.rst7` coordinate files, and writes a `decoy.parm7` topology file using a system call to `tLeap`. It then uses `sander` to run Amber minimization on the `.rst7` files, where the minimization parameters are given in the `min_norestraint.in` file.
    - Minimization were performed using 14SBonlysc force field and GBNeck2 implicit solvent model. XMIN method is used with max cycles of 1000. Minimization will be stopped if the root-mean-square of the Cartesian elements of the gradients is less than 0.01 kcal/mol.

- **Expected Output**
    - A `../work/AmberMinimize/` directory.
        - 50 `minbatch_*sh` scripts.
        - `.rst7` files for each of the decoys in the `4.FastRelax_LoopandMutantsPlusNeighbs/` directory.
        - one `decoy.parm7` file.
        - After the minimization scripts have run,
            - 5000 `min*.rst7` files.


#### 6. Evaluate the Amber energies:

```bash
# Before running script, change BASE_DIR to the dir above the methods folder.

python 6.GetAmberEnergies.py
```

- **Description**  
    - This script evaluates the Amber energies for all decoys in the `5.AmberMinimize/` directory and writes them to a score file.

- **Expected Output**
    - An `../work/AmberScores.sc` file.

#### Choose the best structure:
