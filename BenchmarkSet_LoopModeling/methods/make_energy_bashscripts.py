import os, sys

def chunks(l,n):
    n = max(1,n)
    return [l[i:i+n] for i in range(0, len(l), n)]

def main(pdblist):

    setchunks = chunks(pdblist, 5)

    count = 0
    for chunk in setchunks:
        count += 1
        with open('GetScores_%i.sh' % count, 'w') as scorefile:
            scorefile.write('#!/bin/bash\n#SBATCH -n 1\n#SBATCH -c 1\n#SBATCH -o L_{C}.out\n#SBATCH --job-name=L_{C}\n'.format(C=str(count) ) )
            scorefile.write('source activate py27\nsource /scratch/kmb413/amber_jan142016/amber.sh\n')
            for input_pdb in chunk:
                input_pdb = input_pdb[0:4]

                ## Decoy Scoring
                scorefile.write("python 5.Amber_GetEnergies.py -i {native} -o {native}_amber.sc \n".format( native=input_pdb ))

if __name__ == '__main__':
    pdblist_ = sys.argv[1]

    if os.path.isfile(pdblist_):
        with open(pdblist_) as fh:
            PDBLIST = fh.read().split()
    else:
        PDBLIST = pdblist_.split(',')

     main(pdblist=PDBLIST)


