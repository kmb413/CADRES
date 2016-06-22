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
- **1.score.sh** Score and clean all input pdbs
- **2.preprocess.sh** Generate mutfiles and lengthen peptides 
    - **gen_mutfile_pdbs.py** helper script for above
- **3.pre_min.sh** Preminimizes complex for ddg
- **3.fpd_prepack.sh** Prepacks complex for flexpepdock
- **4.ddg.sh**
- **5.fpd_refine.sh**
- **6.fpd_postprocess.sh**
    - **select_fpd_results.py** helper script for above
- **7.ddg_rmsd.sh**
    - **xmls/ddg_rmsd.xml** helper script for above

***Amber Run***
- **8.generate_rst7_parm7_files.py** Generate topology and resart files for Amber minimization
- **9.amber_minimization.py** Run minimization
    - **min.in** helper script for above
- **10.run_mmgbsa.py** Get AMBER Binding energies as Ebound - Edomain - Epeptide
- **11.decomp_single.py** Get AMBER per-residue energies
    - **mmgbsa.in** helper script for above
- **12.process_residue.py** Get AMBER per-residue energies averaged over 50 snapshots

***Wrapper/helper scripts***
- **13.get_interaction_energy.sh** Find interaction energy for both Amber and Rosetta
    - **xmls/InterfaceSelector.xml** helper script for above
    - **get_average_amber_energy.pl** helper script for above
- **14.postprocess_ddg.py** Find ddg given several variations of dg's for both Amber and Rosetta
- **utils.py** Used in Amber run
- **decomp_mpi.py** Can be used to wrap decomp_single as mpi run
- **get_energy_each_snapshot.py** Not currently in use
- **driver.sh** List of commands used to run entire Rosetta protocol
- **loop_pdbs.sh** Used to wrap all Rosetta scripts

Instructions
============

#### First, set environment variables to appropriate values (or add them to each script manually)

```bash
export ROSETTA_BIN=~/Rosetta/main/source/bin/
export ROSETTA_SRC=~/Rosetta/main/source/src/
export ROSETTA_DB=~/Rosetta/main/database/
export OUTPATH=~/git_repos/cadres_submissions/.../output/
export INPATH=~/git_repos/cadres_submissions/.../input/
export SCRIPTS=~/git_repos/cadres_submissions/.../methods/
export RESULTS=~/git_repos/cadres_submissions/.../results/
```
#### 1. Clean and renumber all pdbs in $INPATH'/input_pdbs/'

```bash

bash 1.score.sh $INPATH'/input_pdbs/1be9_complex.pdb' 1be9_complex 1be9 $INPATH'/input_pdbs/'
#Usage: bash 1.score.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath>
```

- **Expected Output**
    - Replaced pdb with new renumbered, cleaned pdb. 
    - If this pdb did not exist in orig_pdb, moved it there. 

#### 2. Generate mut_file and lengthen peptide as necessary for all *_complex.pdbs in $INPATH'/input_pdbs/'

```bash

bash 2.preprocess.sh $INPATH'/input_pdbs/1be9_complex.pdb' 1be9_complex 1be9 $INPATH'/input_pdbs/'
#Usage: bash 2.preprocess.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath>
```

- **Necessary Input**
    - $INPATH/list_seqs/all_seqs_data.tsv
    - $INPATH/list_seqs/1be9.list

- **Expected Output**
    - $INPATH/mut_file/[pdb_id][pept_length]_complex.mutfile
    - $INPATH/mut_file/[pdb_id].rc - record id and other information correspondence file for each pdb
    - $INPATH/input_pdbs/[pdb_id][pept_length]_complex.pdb

#### 3. Pre-minimize all ????.pdb files in $INPATH/input_pdbs/ so as to generate constraint files

```bash

bash 3.pre_min.sh $INPATH'/input_pdbs/1be9.pdb' 1be9 1be9 $OUTPATH'/pre_min1/' $INPATH'/input_pdbs/' 
#Usage: bash 3.pre_min.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath> <cst_outpath>
```

- **Expected Output**
    - $OUTPATH/pre_min1/min_[pdb]_0001.pdb 
    - $INPATH/input_pdbs/[pdb].cst

#### 3. Pre-minimize all ??????_*complex.pdb files in $INPATH/input_pdbs/ for input to ddg (may not be strictly necessary but it is already part of our pipeline)

```bash

bash 3.pre_min.sh $INPATH'/input_pdbs/1be908_complex.pdb' 1be908_complex 1be9 $OUTPATH'/pre_min1/' $INPATH'/input_pdbs/'
#Usage: bash 3.pre_min.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath> <cst_outpath>
```

- **Expected Output**
    - $OUTPATH/pre_min1/min_[pdb][pept_length]_complex_0001.pdb
    - $INPATH/input_pdbs/[pdb][pept_length]_complex.cst

#### 3. Pre-pack all min_??????_*complex_0001.pdb files in $OUTPATH/pre_min1/ for input to flexpepdock 

```bash

bash 3.fpd_prepack.sh $OUTPATH'/pre_min1/min_1be908_complex_0001.pdb' min_1be908_complex_0001 1be9 $OUTPATH'/prepack/' "-cst_fa_file $INPATH'/'input_pdbs/1be9.cst"
#Usage: bash 3.pre_min.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath> <cst_file_param>
```

- **Expected Output**
    - $OUTPATH/prepack/min_[pdb][pept_length]_complex_0001min_[pdb][pept_length]_complex_0001_0001.pdb

#### 3. Pre-minimize all files in $OUTPATH/prepack/ for input to ddg. Minimize bb and sc.

```bash

bash 3.pre_min.sh $OUTPATH'/prepack/min_1be908_complex_0001min1be908_complex_0001_0001.pdb' min_1be908_complex_0001min1be908_complex_0001_0001 1be9 $OUTPATH'/pre_min2/' "-cst_fa_file $INPATH'/'input_pdbs/1be9.cst"
#Usage: bash 3.pre_min.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath> <cst_file_param>
```

- **Expected Output**
    - $OUTPATH/pre_min2/min_min_[pdb][pept_length]_complex_0001min_[pdb][pept_length]_complex_0001_0001_0001.pdb

#### 4. Run ddg on all files in $OUTPATH/pre_min2/ to generate mutated pdb files (50 per pdb) - takes up 10 cores at a time with 5 iterations per core.

```bash
bash 4.ddg.sh $OUTPATH'/pre_min2/min_min_1be908_complex_0001min1be908_complex_0001_0001_0001.pdb' min_min_1be908_complex_0001min1be908_complex_0001_0001_0001 1be9 $OUTPATH'/ddg/' "-cst_fa_file $INPATH'/'input_pdbs/1be9.cst" 1
#Usage: bash 4.ddg.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath> <cst_file_param> <server_id_number>
```

- **Expected Output**
    - $OUTPATH/ddg/min_min_[pdb][pept_length]_complex_0001min_[pdb][pept_length]_complex_0001_0001_0001/ directory
    	- $i/ directories inside it, with i representing 1-10
	     - each directory has files associated with running ddg 5 times
        - for each mutated sequence, three associated pdb files (the three with the lowest energies) are extracted to the top level directory

#### 5. Run flexpepdock refine on all files in $OUTPATH/ddg/*/*.pdb to generate diversity per sequence - takes up 10 cores at a time with 1 (for NMR ensembles) or 20 nstruct per core.
todo what is filename?
```bash 
bash 5.fpd_refine.sh $OUTPATH'/ddg/min_min_1be908_complex_0001min1be908_complex_0001_0001_0001/*.pdb' filename 1be9 $OUTPATH'/refine/' "-cst_fa_file $INPATH'/'input_pdbs/1be9.cst" 1 0
#Usage: bash 5.fpd_refine.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath> <cst_file_param> <server> <nmr>
```     

- **Expected Output**
    - $OUTPATH/refine/[pdb][pept_length]_[mut_seq]/ directory
        - $prefix_$i/ directories inside it, with i representing 1-10 and prefix representing unique identifier for each sequence of the top 3 identified in the step before.
             - each directory has files associated with running fpd, including output pdb files

#### 6. Postprocess fpd results to choose 50 pdbs from along the bottom of the energy funnel (i.e. distributed in rmsd over lowest 10% energy)  

```bash
bash 6.fpd_postprocess.sh $OUTPATH'/refine/1be908_wt/' 1be908_wt 1be908 $OUTPATH'/refine/'
#Usage: bash 4.ddg.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath>
``` 

- **Expected Output**
    - 50 files labeled $OUTPATH/refine/[pdb][pept_length]_[mut_seq]/[prefix]_[mut|repacked]_[seq|wt]_round_[suffix].pdb

#### 7. Evaluate dg as binding energy (Ebound - Edomain - Epept) and retrieve rmsd from native 

```bash
bash 7.ddg_rmsd.sh $OUTPATH'/refine/1be908_wt/' 1be908_wt 1be9 $OUTPATH'/ddg_csv/rosetta/' 
#Usage: bash 4.ddg.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath>
```

- **Expected Output**
    - $OUTPATH/ddg_csv/rosetta/[pdb][pept_length]_[mut_seq].csv 

#### 8. Generate topology and resart files for AMBER minimization

    ```bash
    export root_dir=/project1/dacase-001/haichit/rosseta_amber/pdz/PDZ_ddG/results/refine/
    export pdb_folder=1be908_wt
    python scripts/generate_rst7_parm7_files.py $pdb_folder $root_dir

    # $pdb_folder: folder that have all original pdb files
    # $root_dir: where you have $pdb_folder
    # This script will create a $pdb_folder in this current dir
    # and generate AMBER's topology and restart files for minimization.
    # For demonstration, I kept only a single pdb file, rst7 and prmtop in ./1be908_wt folder
    ```

#### 9. Run AMBER minimization

    ```bash
    cd 1be908_wt
    python ../scripts/amber_minimization.py -p prmtop -c "NoH*.rst7" -i ../input/min.in

    # minimized coordinate filename: min*rst7
    ```

#### 10. Get AMBER ddG by running MMGBSA method

    ```bash
    cd 1be908_wt
    mkdir mmgbsa
    cd mmgbsa
    python ../../scripts/run_mmgbsa.py

    # ddG.csv file will be created

    # Expectation: AMBER's ddG (kcal/mol) for demo snapshot
    # min_NoH_9_2_9_9_repacked_wt_round_2_0020.rst7: -63.18075344
    ```
#### 11. Run mmgbsa per residue energy decomposition

    ```bash
    # n_proteins = 87
    # Please update decomp_mpi.py to use correct path
    # That script will look for a pdblist.txt, a folder having all minimized rst7 files
    # Please update it to your need
    mpirun -n 87 python scripts/decomp_mpi.py

    # Otherwise, you can run a single protein
    # ../../../1be908_wt: have min*rst7 and prmtop files
    python ./scripts/decomp_single.py ../../../1be908_wt
    ```

#### 12. Get average energy (from 50 snapshots) for each residue in each protein

   ```bash
   cd 1be908_wt
   python ../scripts/process_residue.py

   # res.csv file will be created
   # tot = vdw  + int + eel + pol + sas

   # int: Internal energy contributions
   # vdw: van der Waals energy contributions
   # eel: Electrostatic energy contributions
   # pol: Polar solvation free energy contributions
   # sas: Non-polar solvation free energy contributions

   # tot: Total free energy contributions (sum of previous 5).
   ```

#### 13. Evaluate interaction energy (two-body energies spanning interface + one-body energies of mutated residues (without ref energies)) for Rosetta and Amber

```bash
bash 13.get_interaction_energy.sh $OUTPATH'/ddg/min_min_1be908_complex_0001min1be908_complex_0001_0001_0001/*.pdb' filename 1be9 $OUTPATH'/refine/' "-cst_fa_file $INPATH'/'input_pdbs/1be9.cst" 1 0
#Usage: bash 5.fpd_refine.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath> <cst_file_param> <server> <nmr>
```  

Methods
-------
- Minimization were performed using 14SBonlysc force field and GBNeck2 implicit solvent model.
XMIN method is used with max cycles of 1000. Minimization will be stopped if the root-mean-square
of the Cartesian elements of the gradients is less than 0.01 kcal/mol.

- The potential energies of final snapshots were then evaluated by `sander` program via its Python interface (`pysander`)

All minimization and energy evaluations were performed with the development version of [AmberTools16](
http://ambermd.org/AmberTools16-get.html)

- See also:

    ```bash
    Section: "Decomposition Data" in http://ambermd.org/doc12/Amber16.pdf (page 675)~                                           
