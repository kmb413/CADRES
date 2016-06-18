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

To run the method on all PDBs in the short-loop set,

- First, unzip the loop_modeling_ngk_r57934.7z archive, which contains all the decoy structures:

    ```bash
    7za loop_modeling_ngk_r57934.7z
    ```

    Note: There exists an extracted loop_modeling_ngk_r57934 folder, but this only contains decoy structures for
    the 1oyc example.

- Minimize the decoy structures using Rosetta:

    ```bash
    python 1.Rosetta_Minimize.py pdblist

    # pdblist is a file containing a list of all 45 short-loop PDB IDs.
    ```
    
    - Description
        
        This script will make a /rosetta_minimization directory in which it will also make
        sub-directories for each of the 45 PDB IDs. In each sub-directory, it will write several
        minimization bash scripts that have a slurm-style queueing system header and the
        minimization command. The minimization scripts will be automatically submitted to the queue
        unless auto_submit is explicitly turned off:

        ```bash
        python 1.Rosetta_Minimize.py pdblist 0
        ```
        If you use this flag, you must cd into each directory and bash each min*.sh script.

        The minimization is carried out via RosettaScripts, where the loop region is minimized
        with BB and SC movements on. The rest of the protein is left fixed.

        Flags: 
            - -score:weights talaris2014 
            - -ex1 -ex2 -extrachi_cutoff 1 
            - -use_input_sc 
            - -nblist_autoupdate
    - Output

        - A /rosetta_minimization/ directory
            - /rosetta_minimization/{PDB_Code} directories
                - min*.sh scripts.
                - {PDB_code}.*.list files, which are lists containing the filepaths to 100 or less
                decoy structures.

        - After the min*.sh scripts have run, 
            - {decoy_pdb}_0001.pdb files
            - score.*.sc files, one for each of the {PDB_code}.*.list files.

- Minimize the decoy structures using Amber:

    ```bash
    python 2.Amber_MinimizationSetUp pdblist
    python 3.Amber_GenerateRST7andParm7.py pdblist
    for pdb in `cat pdblist`
        do
            cd amber_minimization/$pdb
            python ../../4.Amber_RunMinimization.py -p 1oyc.parm7 \
                -O -c "NoH*.rst7" -i min.in
            cd ../../
        done
    ```

- Score the Amber-minimized structures:

    ```bash
    python make_energy_bashscripts.py pdblist
    for SCRIPT in `ls GetScores*.sh`; do sbatch $SCRIPT ; done
    ```

- Choose the 'best' scoring decoy structures using both Amber and Rosetta scores:
