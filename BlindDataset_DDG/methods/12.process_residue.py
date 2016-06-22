#!/usr/bin/env python

import sys
import numpy as np

def main():
    from MMPBSA_mods import API as MMPBSA_API
    
    data = MMPBSA_API.load_mmpbsa_info('_MMPBSA_info')
    decomp_data = data['decomp']['gb']['complex']['TDC']
    
    elist = ['tot', 'vdw', 'int', 'eel', 'pol', 'sas']
    line0 = [','.join(['residue', ] + elist[:]),]

    lines = []
    for residue in sorted(decomp_data.keys()):
        res_data = decomp_data[residue]
        line = str(residue) + ',' + ','.join(str(np.mean(res_data[k])) for k in elist)
        lines.append(line)

    line0.extend(lines)
    content = '\n'.join(line0)
    with open('res.csv', 'w') as fh:
        fh.write(content)


if __name__ == '__main__':
    main()
