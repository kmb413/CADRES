import os, sys
import pytraj as pt
import sander
from glob import glob
from mpi4py import MPI
comm = MPI.COMM_WORLD

BASE_DIR=/scratch/kmb413/CADRES/BlindDataset_StructurePrediction/
SCRIPTS_DIR="{base}/scripts/".format( base=BASE_DIR )
OUTPUT_DIR="{base}/work/AmberMinimize/".format( base=BASE_DIR )

def main(argv):
    args = sys.argv
    scorefile = 'AmberScores.sc'

    decoy_list = glob( "{output}min*.rst7".format( output=OUTPUT_DIR ) )

    print("Decoy List: " + str(len(decoy_list)))
    parmfile = "{output}decoy.parm7".format( output=OUTPUT_DIR )
    
    print("Making Traj.")
    traj = pt.iterload( decoy_list, parmfile )
    print("Getting energies...")
    energy_data = pt.pmap_mpi(pt.energy_decomposition, traj, igb=8)
    print("done!")
    if energy_data:
        ekeys = energy_data.keys()
        ekeys.sort()

        print('Scorefile: ' + scorefile)
        with open(scorefile,'w') as myscorefile:

            header = 'description\t'
            for key in ekeys:
                header += key + '\t'
            myscorefile.write(header +"\n")

            for decoy in range(len(decoy_list)):
                scoreline = decoy_list[decoy]+'\t'
                for key in ekeys:
                    scoreline += "%s\t" % str(energy_data[key][decoy])
                myscorefile.write(scoreline+"\n")

if __name__ == "__main__":
    main(sys.argv[1:])
