#!/usr/bin/env python

from rosetta import *
import os
import argparse

init('-mute core.pack.task core.conformation.Conformation')

def read_sequences(seq_file_name):
    with open(seq_file_name) as sf:
        list_seq_lines = sf.readlines()

    list_seqs = [ seq.strip() for seq in list_seq_lines ]

    return list_seqs

def n_mut_pept(list_seqs):
    '''Given a list of sequences returns a list of the unique lengths of sequences'''
    return list(set([len(x) for x in list_seqs]))

def make_mut_file(list_seqs, length, n_pdz_res, WT_pept, mut_file, orig, pdz_muts=None, offset=0, list_seqs_data=None):
    '''Given a filtered list of sequences, an offset, WT_pept, and mut_file to write to, generates a mutfile for that length sequences'''
    prefix=""
    orig_len_WT = len(WT_pept)
    if len(WT_pept) > length:
	if offset == 0:
	    raise ValueError('the length of chain B in the pdb file is longer than the sequence %s and no offset was provided' % (list_seqs[0]))   
	else: 
	    WT_pept = WT_pept[offset:offset+length]
	    orig_len_WT = len(WT_pept) #change length to be equal to final length if we are only looking at small fragment of chain B (1qav)
    elif len(WT_pept) < length:
        WT_pept = WT_pept[0:1] + ''.join("A" for _ in range(length-len(WT_pept))) + WT_pept[1:]

    total_muts=0
    list_total_muts=[ 0 for _ in list_seqs ]
    list_muts=[ [] for _ in list_seqs ]
    rec_id_corr=[ [sd[0],sd[2]+"_","","",""] for sd in list_seqs_data ]
    
    for seq_ind,(seq,seq_data) in enumerate(zip(list_seqs, list_seqs_data)):
        if pdz_muts is not None and pdz_muts[seq_ind] != "Wildtype":
            mut = pdz_muts[seq_ind]

            wt_res = mut[0]
            mut_res = mut[-1]
            pdb_pos = int(mut[1:-1])

            #have to extract pose_position from orig_pdb
            pose_pos = orig.pdb_info().pdb2pose("A",pdb_pos)

            #add correct information to lists
            list_muts[seq_ind].append("{0} {1} {2}\n".format(wt_res, pose_pos, mut_res))
            list_total_muts[seq_ind] = list_total_muts[seq_ind] + 1
            total_muts = total_muts + 1

        for res_ind, (WT, mut) in enumerate(zip(WT_pept, seq), n_pdz_res+1+offset):
	    if WT != mut:
		list_muts[seq_ind].append("{0} {1} {2}\n".format(WT, res_ind, mut))
                list_total_muts[seq_ind] = list_total_muts[seq_ind] + 1
                total_muts = total_muts + 1
        #check if wildtype.  determined by being non-blind and having a ddg of 0 or by being blind and being the same peptide as in pdb
        if ( len(seq_data) == 7 and float(seq_data[5]) == 0.0 ) or ( len(seq_data) == 4 and len(list_muts[seq_ind]) == 0 ):
            rec_id_corr[seq_ind][1] = rec_id_corr[seq_ind][1] + "wt"
        else:
	    rec_id_corr[seq_ind][1] = rec_id_corr[seq_ind][1] + "mut"

        if len(list_muts[seq_ind]) == 0:
            rec_id_corr[seq_ind][2] = "{0}{1:02d}_wt".format(os.path.basename(mut_file)[0:4], orig_len_WT)
        else:
	    rec_id_corr[seq_ind][2] = "{0}_".format(os.path.basename(mut_file)[0:6]) + ''.join([ ''.join(m.split()) for m in list_muts[seq_ind] ] )

	if len(seq_data) == 7:
            rec_id_corr[seq_ind][3] = seq_data[5]
	    rec_id_corr[seq_ind][4] = seq_data[6]
    #take out any cases where list_total_muts is 0
    ind = [ i for i,tot_muts in enumerate(list_total_muts) if tot_muts != 0 ]
    list_total_muts = [ list_total_muts[i] for i in ind ]
    list_muts = [ list_muts[i] for i in ind ]
	

    with open(mut_file, 'w') as mf:
	mf.write("total {0}\n".format(total_muts))
        for seq_ind in xrange(0, len(list_total_muts)):
            mf.write("{0}\n".format(list_total_muts[seq_ind]))
            for item in list_muts[seq_ind]:
		mf.write(item)

    return rec_id_corr

def lengthen_pose(chains, length, pdb_name):
    '''Given an input pose of pdz domain complexed with peptide (numbering should be pose numbering) and n of residues to add
    generates lengthened pose where extra residues are added before N-terminus of peptide. Does not shorten peptide'''

    pdz = chains[1].clone()
    peptide = chains[2].clone()

    n_pdz = pdz.total_residue()
    n_pept = peptide.total_residue()

    n_to_add = length - n_pept
    
    seq_template = ''.join("A" for _ in range(n_to_add+2))
    pose = pose_from_sequence(seq_template)

    newpose = Pose()

    newpose.append_residue_by_jump(peptide.residue(n_pept), newpose.total_residue(), "", "", 0)

    for pept_ind in xrange(n_pept-1, 1, -1):
        newpose.prepend_polymer_residue_before_seqpos(peptide.residue(pept_ind), 1, 0)

    for new_res in xrange(n_to_add+1, 1, -1):
        newpose.prepend_polymer_residue_before_seqpos(pose.residue(new_res), 1, 1)

    newpose.prepend_polymer_residue_before_seqpos(peptide.residue(1), 1, 1)

    pdz.append_pose_by_jump(newpose, pdz.total_residue(), "", "")

    for pept_ind in xrange(n_pdz+1+n_to_add, n_pdz, -1):
        pdz.set_psi(pept_ind, 180.0)
        pdz.set_phi(pept_ind, 180.0)
        pdz.set_omega(pept_ind, 180.0)

    pdz.dump_pdb(pdb_name)
		

def main(in_pdb, orig_pdb_path, list_seqs_file, all_seqs_data, mut_file_path):
    root, ext = os.path.splitext(in_pdb)	 
    pdb_path, pdb_id = os.path.split(root)

    orig_pdb = orig_pdb_path + "/" + pdb_id + ".pdb"
    orig = pose_from_pdb(orig_pdb)

    complex_pose = pose_from_pdb(in_pdb)
    chains = complex_pose.split_by_chain()
    n_pdz_res = chains[1].total_residue()
 
    list_seqs = read_sequences(list_seqs_file)
    
    list_seqs_data = [ s.split('\t') for s in read_sequences(all_seqs_data) if s.split('\t')[2] == pdb_id[0:4].upper() ]
 
    pdz_muts = None

    if "offset" in list_seqs[0]: 
	offset_line = list_seqs.pop(0)
        offset = int(offset_line.split()[1])
    else:
	offset = 0

    #if mutations on PDZ domain as well:
    if len(list_seqs[0].split()) > 1:
        pdz_muts = [ s.split()[0] for s in list_seqs ]
	list_seqs = [ s.split()[1] for s in list_seqs ]

    list_lengths = n_mut_pept(list_seqs)

    WT_pept = chains[2].sequence()

    rec_id_corr = []

    for length in list_lengths:
        filename="/{0}{1:02d}{2}".format(pdb_id[0:4],length,pdb_id[4:])

        #filtering lists of seqs
	indices = [ i for i, s in enumerate(list_seqs) if len(s) == length ]
	list_seqs_filt = [ list_seqs[i] for i in indices ]
        #only possible because list_seqs was created in same order as list_seqs_data
	list_seqs_data_filt = [ list_seqs_data[i] for i in indices ]
        #if there are mutations on PDZ domain then include mutations in mutfile
        #ignore chain because we assume that PDZ domain is chain A
	if pdz_muts is not None:
	    pdz_muts_filt = [ pdz_muts[i] for i in indices ]
            rec_id_corr.extend(make_mut_file(list_seqs_filt, length, n_pdz_res, WT_pept, mut_file_path + filename + ".mut_file", orig, pdz_muts=pdz_muts_filt, offset=offset, list_seqs_data=list_seqs_data_filt))

	#if there are no mutations then only include peptide sequence mutations
        else:
            rec_id_corr.extend(make_mut_file(list_seqs_filt, length, n_pdz_res, WT_pept, mut_file_path + filename + ".mut_file", orig, offset=offset, list_seqs_data=list_seqs_data_filt))

	lengthen_pose(chains, length, pdb_path + filename + ".pdb")

    with open(mut_file_path + pdb_id[0:4] + ".rc", 'w') as rc:
        for item in rec_id_corr:
	    last_item = ",{0},{1}".format(item[3],item[4]) if item[3] != "" else ""
            rc.write("{0},{1},{2}{3}\n".format(item[0], item[1], item[2], last_item))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--in_pdb', help="name of pdb input file with full path")
    parser.add_argument ('--orig_pdb_path', help="name of path for orig pdbs")
    parser.add_argument ('--list_seqs_file', help="name of file with sequences")
    parser.add_argument ('--all_seqs_data', help="name of file with all sequence data in tsv format")
    parser.add_argument ('--mut_file_path', help="name of path for output mut_files")

    args = parser.parse_args()

    main(args.in_pdb, args.orig_pdb_path, args.list_seqs_file, args.all_seqs_data, args.mut_file_path) 
