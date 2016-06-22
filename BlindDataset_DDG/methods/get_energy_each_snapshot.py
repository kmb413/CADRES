#!/usr/bin/env python

import sys

def main():
    from MMPBSA_mods import API as MMPBSA_API
    
    data = MMPBSA_API.load_mmpbsa_info('_MMPBSA_info')
    decomp_data = data['decomp']['gb']['complex']['TDC']

    for residue in decomp_data:
        energy_term = 'tot'
        print('res = {}, energy={}'.format(residue, decomp_data[residue][energy_term]))

if __name__ == '__main__':
    main()
