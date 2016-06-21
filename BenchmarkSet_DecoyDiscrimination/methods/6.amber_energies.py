import sys
import pytraj as pt
from glob import glob

def main():
    folder = sys.argv[1]
    files = glob('{}/min*rst7'.format(folder))
    parm = glob("{}/*.parm7".format(folder))[0]
    
    traj = pt.iterload(files, top=parm)
    
    energies = pt.energy_decomposition(traj, igb=8)['tot']
    for fn, potential in zip(files, energies):
        print(fn, potential)

if __name__ == '__main__':
    """python scripts/eamber_single.py 1a32
    """
    main()
