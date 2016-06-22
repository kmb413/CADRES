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
#### Then clean and renumber all pdbs in $INPATH'/input_pdbs/'

```bash

bash 1.score.sh $INPATH'/input_pdbs/1be9_complex.pdb' 1be9_complex 1be9 $INPATH'/input_pdbs/'
#Usage: bash 1.score.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath>
```

- **Expected Output**
    - Replaced pdb with new renumbered, cleaned pdb. 
    - If this pdb did not exist in orig_pdb, moved it there. 

#### Generate mut_file and lengthen peptide as necessary for all *_complex.pdbs in $INPATH'/input_pdbs/'

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

#### Pre-minimize all ????.pdb files in $INPATH/input_pdbs/ so as to generate constraint files

```bash

bash 3.pre_min.sh $INPATH'/input_pdbs/1be9.pdb' 1be9 1be9 $OUTPATH'/pre_min1/' $INPATH'/input_pdbs/' 
#Usage: bash 3.pre_min.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath> <cst_outpath>
```

- **Expected Output**
    - $OUTPATH/pre_min1/min_[pdb]_0001.pdb 
    - $INPATH/input_pdbs/[pdb].cst

#### Pre-minimize all ??????_*complex.pdb files in $INPATH/input_pdbs/ for input to ddg (may not be strictly necessary but it is already part of our pipeline)

```bash

bash 3.pre_min.sh $INPATH'/input_pdbs/1be908_complex.pdb' 1be908_complex 1be9 $OUTPATH'/pre_min1/' $INPATH'/input_pdbs/'
#Usage: bash 3.pre_min.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath> <cst_outpath>
```

- **Expected Output**
    - $OUTPATH/pre_min1/min_[pdb][pept_length]_complex_0001.pdb
    - $INPATH/input_pdbs/[pdb][pept_length]_complex.cst

#### Pre-pack all ??????_*complex.pdb files in $OUTPATH/pre_min1/ for input to flexpepdock 

```bash

bash 3.fpd_prepack.sh $OUTPATH'/pre_min1/min_1be908_complex_0001.pdb' min_1be908_complex_0001 1be9 $OUTPATH'/prepack/' "-cst_fa_file $INPATH'/'input_pdbs/1be9.cst"
#Usage: bash 3.pre_min.sh <full_path_to_pdb_file> <actual_name_pdb_file_noext> <pdb_id> <outpath> <cst_file_param>
```

- **Expected Output**
    - $INPATH/prepack/min_[pdb][pept_length]_complex_0001.pdb
    - $INPATH/input_pdbs/[pdb][pept_length]_complex.cst

	#performing flexpepdock prepack - only locally
	$SCRIPTS'/'loop_pdbs.sh $OUTPATH'/pre_min1/*_complex*.pdb' $OUTPATH'/'prepack'/' "" 4 6 $SCRIPTS'/'fpd_prepack.sh

        #performing a second pre_min (bb as well as sc) to prepare for ddg
        $SCRIPTS'/'loop_pdbs.sh $OUTPATH'/prepack/*.pdb' $OUTPATH'/'pre_min2'/' "" 4 6 $SCRIPTS'/'pre_min.sh

else
	#run ddg on pre_min pdbs
	$SCRIPTS'/'loop_pdbs.sh $OUTPATH'/pre_min2/*.pdb' $OUTPATH'/'ddg'/' "" 8 14 $SCRIPTS'/'ddg.sh $server 5 10

	#performing flexpepdock refine for 1g9o - only on server 
        #only one server because already partitioned the pdbs in the previous step
	$SCRIPTS'/'loop_pdbs.sh $OUTPATH'/ddg/*/*.pdb' $OUTPATH'/refine/' "" 8 6 $SCRIPTS'/'fpd_refine.sh 1 1 10

	$SCRIPTS'/'loop_pdbs.sh $OUTPATH'/refine/*/' $OUTPATH'/refine/' "" 0 6 $SCRIPTS'/'fpd_postprocess.sh 1 1 1 

        $SCRIPTS'/'loop_pdbs.sh $OUTPATH'/refine/*/' $OUTPATH'/ddg_csv/rosetta/' "" 0 4 $SCRIPTS'/'ddg_rmsd.sh $server 5 1

fi

### To run the method on all decoys in silent files for a given set (e.g. decoys.set1 or decoys.set2)

#### 1. place the silent files in $BASEDIR/input/decoys.set<set_number>
#### 2. extract pdbs from the silent files

- Script for one silent file

    ```bash
    1.extract.sh $BASEDIR/input/decoys.set1/ 1a32.1000.out $BASEDIR/input/decoys.set1/1a32/ 1a32
    ```

- Wrapper script to extract all silent files when run on one server with at least 40 cores available (can change n_cores in the script itself)

    ```bash
    loop_pdbs.sh $BASEDIR/input/decoys.set1/ "*.out" $BASEDIR/input/decoys.set1/ 0 1.extract.sh 1 1 talaris2014 1
    ```

- **Description**
    - This script will make a `../output/rosetta_minimization directory` in which it will also make
sub-directories for each of the 45 PDB IDs. In each sub-directory, it will write several
minimization bash scripts that have a slurm-style queueing system header and the
minimization command. The minimization scripts will be automatically submitted to the queue
unless auto_submit is explicitly turned off:

        ```bash
        python 1.Rosetta_Minimize.py ../input/pdblist 0
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
    - A `../output/rosetta_minimization/` directory
        - `../output/rosetta_minimization/{PDB_Code}` directories
            - `min*.sh` scripts.
            - `{PDB_code}.*.list` files, which are lists containing the filepaths to 100 or less decoy structures.

            - After the min*.sh scripts have run,
                - `{decoy_pdb}_0001.pdb` files
                - `score.*.sc files`, one for each of the `{PDB_code}.*.list` files.

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

- Generate topology and resart files for AMBER minimization

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

- Run minimization

    ```bash
    cd 1be908_wt
    python ../scripts/amber_minimization.py -p prmtop -c "NoH*.rst7" -i ../input/min.in

    # minimized coordinate filename: min*rst7
    ```

- Get AMBER ddG by running MMGBSA method

    ```bash
    cd 1be908_wt
    mkdir mmgbsa
    cd mmgbsa
    python ../../scripts/run_mmgbsa.py

    # ddG.csv file will be created

    # Expectation: AMBER's ddG (kcal/mol) for demo snapshot
    # min_NoH_9_2_9_9_repacked_wt_round_2_0020.rst7: -63.18075344
    ```
- Run mmgbsa per residue energy decomposition

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

- Get average energy (from 50 snapshots) for each residue in each protein

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

- Get total energy for each residue for each snapshot

    ```bash
    cd 1be908_wt
    python ../scripts/get_energy_each_snapshot.py
    ```

- See also:

    ```bash
    Section: "Decomposition Data" in http://ambermd.org/doc12/Amber16.pdf (page 675)

Methods
-------
- Minimization were performed using 14SBonlysc force field and GBNeck2 implicit solvent model.
XMIN method is used with max cycles of 1000. Minimization will be stopped if the root-mean-square
of the Cartesian elements of the gradients is less than 0.01 kcal/mol.

- The potential energies of final snapshots were then evaluated by `sander` program via its Python interface (`pysander`)

All minimization and energy evaluations were performed with the development version of [AmberTools16](
http://ambermd.org/AmberTools16-get.html)
~                                           
