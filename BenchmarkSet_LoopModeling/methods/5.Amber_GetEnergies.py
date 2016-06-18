import pytraj as pt
import sander
import os, sys, getopt
from glob import glob
from mpi4py import MPI
import pandas as pd

loopdef = pd.read_json('loopdefs.json')

# create mpi handler to get cpu rank
comm = MPI.COMM_WORLD

##############
BASE_DIR    =  "/scratch/kmb413/CADRES/BenchmarkSet_LoopModeling/methods"
NATIVES_DIR =  "{base_directory}/Natives".format( base_directory=BASE_DIR )
AMBERMIN_DIR = "{base_directory}/amber_minimization".format( base_directory=BASE_DIR )
#############

try:
    os.mkdir('{base_directory}/amber_minimization/AmberScores/'.format( base_directory=BASE_DIR ) )
except OSError:
    pass

def chunks(l,n):
    n = max(1,n)
    return [l[i:i+n] for i in range(0, len(l), n)]

def get_ca_rmsd( traj, mask, metric ):
    
    ca_rmsd = pt.pairwise_rmsd(traj, mask=mask, metric=metric)
    #ca_rmsd = pt.pmap_mpi(pt.rmsd, traj, mask='@CA')

    return ca_rmsd;

def get_energies( traj, igb_value ):

    #energy_data = pt.energy_decomposition(traj, igb=8)
    energy_data = pt.pmap_mpi(pt.energy_decomposition, traj, igb=igb_value )
    return energy_data;


def get_energy_term( traj, term ):

    energy_data = pt.pmap_mpi(pt.energy_decomposition, traj, igb=8)
    return energy_data[term];


def main(argv):
    args = sys.argv

    input_pdb = ''
    outfile = ''

    try:
        opts, args=getopt.getopt(sys.argv[1:], "ho:i:o:", ["in:file:i=", "out:file:scorefile="])
    except getopt.GetoptError:
        print('Unknown flag given.\nKnown flags:\n\t-h\n\t-n <native>')
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print('Something.py --in:file:s <input_pdb_id> --out:file:scorefile <output_filename>')
            sys.exit()
        elif opt in ("-i", "--in:file:i"):
            input_pdb = arg
        elif opt in ("-o", "--out:file:scorefile"):
            outfile = arg

    if input_pdb == '':
        print('ERROR: No PDB ID supplied.')
        sys.exit()
    elif len(input_pdb) != 4:
        print("ERROR: Input PDB should be 4 letter PDB code.")
        sys.exit()
    input_pdb = input_pdb.lower()

    if outfile == '':
        outfile = 'Scores.sc'

    ######################################################################
    ######################################################################

    print( "===== Native RST7: {PDB} =====".format(PDB=input_pdb) )

    #Native is crystal structure.
    native_rst7 = NATIVES_DIR +"/{PDB}.rst7".format( PDB=input_pdb )
    native_parm = NATIVES_DIR +"/{PDB}.parm7".format( PDB=input_pdb )

    print("Native RST7\t{natrst}".format(natrst=native_rst7))
    print("Native PARM7\t{natparm}".format(natparm=native_parm))

    os.chdir(AMBERMIN_DIR+"/{PDB}/".format( PDB=input_pdb ) )
    print(AMBERMIN_DIR+"/{PDB}/".format( PDB=input_pdb ) )
    min_decoys = glob('min*.rst7')  ## List of rst7s ["<rst7_1>", "<rst7_2>", ...]

    print("== Analyzing %i mols==" % len(min_decoys))

    min_decoys.insert(0, native_rst7)

    print("\t=== Loading Trajectories ===")
    traj = pt.iterload(min_decoys, native_parm)
    print(traj)

    print("\t=== Getting RMSDs ===")
    ca_mask = '@CA & :{loop_start}-{loop_end}'.format(loop_start=int(loopdef[input_pdb]['StartResidueID'].strip()), loop_end=int(loopdef[input_pdb]['EndResidueID'].strip() ))
    print ca_mask

    ca_rmsd_nofit = get_ca_rmsd( traj, ca_mask, 'nofit' )
    ca_rmsd_fit = get_ca_rmsd( traj, ca_mask, 'rms' )

    print("\t=== Getting Energy Decomposition ===")
    energy_data = get_energies( traj, 8 )
    print("\t\tFinished")
    
    if energy_data:

        energy_data['rmsd'] = ca_rmsd_nofit[0]
        energy_data['rmsd_suploop'] = ca_rmsd_fit[0]

        ekeys = energy_data.keys()
        ekeys.sort()

        print("Outfile: " + outfile)
        with open(outfile,'w') as scorefile:
            header = 'description\t'
            for key in ekeys:
                header += key + '\t'
            scorefile.write(header+"\n")

            for pdb_index in range(len(min_decoys)):
                scoreline = min_decoys[pdb_index]+'\t'
                for key in ekeys:
                    scoreline += '%s\t' % str(energy_data[key][pdb_index])
                scorefile.write(scoreline+"\n")

if __name__ == "__main__":
    main(sys.argv[1:])
