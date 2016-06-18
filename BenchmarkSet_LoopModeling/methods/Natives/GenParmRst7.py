##Generate rst7 files and parm7 files from all clean pdbs in this directory.

import os, sys, getopt

def chunks(l,n):
    n = max(1,n)
    return [l[i:i+n] for i in range(0, len(l), n)]

def main(argv):
    args = sys.argv

    input_pdb = ''

    try:
        opts, args=getopt.getopt(sys.argv[1:], "ho:i:o:", ["in:file:s=", "out:file:scorefile="])
    except getopt.GetoptError:
        print('Unknown flag given.\nKnown flags:\n\t-h\n\t-i <input_pdb_id>')
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print('Something.py --in:file:s <input_pdb_id> --out:file:scorefile <output_filename>')
            sys.exit()
        elif opt in ("-i", "--in:file:s"):
            input_pdb = arg

    print( "===== PDB: %s =====" % input_pdb )


    ########################################################################
    ### Remove Hydrogens from PDBs ###
    ########################################################################
    #decoys.append( "%s.trimmed.pdb\n" % input_pdb )
    
    os.system("sed '/     H  /d' {native}.clean.pdb > NoH_{native}.clean.pdb".format(native=input_pdb))

    ########################################################################
    ### Create RST7 and PARM7 files from NoH_PDBs. Minimize using Sander ###
    ########################################################################

    with open('tleap.in','w') as tfile:
        tfile.write("source leaprc.ff14SBonlysc\n")
        tfile.write("m = loadpdb NoH_{native}.clean.pdb\n".format(native=input_pdb) )
        tfile.write("set default pbradii mbondi3\n")
        tfile.write("saveamberparm m {native}.parm7 {native}.rst7\n".format(native=input_pdb) )
        tfile.write("quit")

    os.system('tleap -f tleap.in')

    

if __name__ == "__main__":
    main(sys.argv[1:])
