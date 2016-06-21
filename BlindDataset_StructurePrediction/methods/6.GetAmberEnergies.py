import os, sys
import pytraj as pt
import sander
from glob import glob
from mpi4py import MPI
comm = MPI.COMM_WORLD

BASE_DIR="/scratch/kmb413/CADRES/BlindDataset_StructurePrediction/methods"

def main(argv):
    args = sys.argv
    scorefile = 'AmberScores.sc'

    decoy_list = glob( "{base}/5.AmberMinimize/min*.rst7".format( base=BASE_DIR ) )

    print("Decoy List: " + str(len(decoy_list)))
    parmfile = "{base}/5.AmberMinimize/decoy.parm7".format( base=BASE_DIR )
    
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
