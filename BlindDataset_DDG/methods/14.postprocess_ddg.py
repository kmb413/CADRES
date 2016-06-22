#!/usr/bin/env python

import glob
import os
import argparse
import numpy as np
from plot import scatterplot
from plot import conv
from scipy.stats.stats import pearsonr
from scipy.stats.stats import spearmanr

def dominates(row, rowCandidate):
    return all(r <= rc for r, rc in zip(row, rowCandidate))

def cull(pts, dominates):
    dominated = []
    cleared = []
    remaining = pts
    while remaining:
        candidate = remaining[0]
        new_remaining = []
        for other in remaining[1:]:
            [new_remaining, dominated][dominates(candidate, other)].append(other)
        if not any(dominates(other, candidate) for other in new_remaining):
            cleared.append(candidate)
        else:
            dominated.append(candidate)
        remaining = new_remaining
    return cleared, dominated

def gen_ranks(list_energies):
    indices = list(range(len(list_energies)))
    indices.sort(key=lambda x: list_energies[x])
    output = [0] * len(indices)
    for i, x in enumerate(indices):
        output[x] = i
    return output

def find_pareto(csv_list1, csv_list2):

    comb = [ (dg,dg2) for k,dg,r in csv_list1 for k2,dg2,r2 in csv_list2 if k == k2 ]
    list_dgs1 = [ d1 for d1, d2 in comb ]
    list_dgs2 = [ d2 for d1, d2 in comb ]

    ranks1 = gen_ranks(list_dgs1)
    ranks2 = gen_ranks(list_dgs2)

    pts = map(list, zip(ranks1, ranks2))

    cleared, dominated = cull(pts, dominates)

    cleared_d = dict(cleared)
    pts_r = zip(ranks1,ranks2,list_dgs1,list_dgs2)

    pareto_equal_min = min([ e1+e2 for e1,e2 in cleared_d.items() ])
    list_pts =  [ (r1,r2,l1,l2) for r1, r2, l1, l2 in pts_r if r1+r2 == pareto_equal_min ]
    avg_min_dg = find_lowest_point( list_pts )

    return avg_min_dg

def find_lowest_point( list_pts ):
    first_rank_list = [ p[0] for p in list_pts ]
    second_rank_list = [ p[1] for p in list_pts ]
    min_rank = min(first_rank_list + second_rank_list)
    min_point = [ (l1,l2) for r1, r2, l1, l2 in list_pts if min_rank == r1 or min_rank == r2 ][0]
    avg = (min_point[0] + min_point[1]) / 2.0
    return avg

def read_csv_dict(csv_file_name):
    with open(csv_file_name) as c:
        lines = c.readlines()

    csv_dict = dict( (l.strip().split(',')[0], l.strip().split(',')[1:] ) for l in lines )

    return csv_dict

def read_csv_list(csv_file_name, protocol=None):
    with open(csv_file_name) as c:
        lines = c.readlines()


    csv_list = [ l.strip().split(',') for l in lines ]
    if protocol == "rosetta":
        csv_list = [ [l[0][0:-5]] + [float(l[1])/1.0] + l[2:] for l in csv_list ]
    elif protocol == "amber":
        csv_list = [ [l[0][38:-5]] + [float(l[1])/2.0] + l[2:]  for l in csv_list ]

    
    return csv_list

def get_mean(csv_dict):
    mean_dg = np.mean([ float(dg) for key, dg, rmsd in csv_dict ])
    return mean_dg 

def get_bottom3(csv_dict):
    bottom3_dg = np.mean(sorted([float(dg) for key,dg,rmsd in csv_dict])[0:3])
    return bottom3_dg

def get_mean_csv(csv_name,protocol=None):
    return get_mean(read_csv_list(csv_name, protocol=protocol))

def get_bottom3_csv(csv_name,protocol=None):
    return get_mean(read_csv_list(csv_name, protocol=protocol))

def get_mean_txt(txt_name,protocol=None):
    with open(txt_name) as t:
        m = float(t.readlines()[0].strip())
    return m

def main(rec_corr_path, ddg_path, amber_pdb_path, rosetta_pdb_path, out_csv_path):
    amber_csv_path = os.path.join(ddg_path, "amber")
    rosetta_csv_path = os.path.join(ddg_path, "rosetta")
    amber_inter_mean_path = os.path.join(ddg_path, "amber_inter_mean")
    rosetta_inter_mean_path = os.path.join(ddg_path, "rosetta_inter_mean")
    rosetta_inter_path = os.path.join(ddg_path, "rosetta_inter")


    #Plots to generate
    #Per pdb - known ddg vs. many diff protocols, each with their own row.  A protocol may have more than one plot depending on filtering method (i.e. mean, bottom 3, pareto)
    #For all pdbs - pred rosetta corr values vs. many diff protocols, each with their series color.  A protocol may have more than one plot depending on filtering method (i.e. mean, bottom 3, pareto).  3 rows one for each corr value
    #For all pdbs - known ddg vs. many diff protocols, each with their own row. A protocol may have more than one plot depending on filtering method (i.e. mean, bottom 3, pareto)

    list_rec_corr_names = glob.glob(rec_corr_path + "*.rc")

    #corr_values_dict has the following shape - "Pred" : { "Pred" : [ddg_vals] }, "Amber" : { "Mean.." : [ddg_vals], "Bott.." : [ddg_vals]}, "Rosetta" : { "Mean.." : [ddg_vals], "Bott.." : [ddg_vals]} 
    corr_values_dict = {}
    
    all_amber_ddg_dict = {}
    all_rosetta_ddg_dict = {}
    all_known_ddg_dict = {}
    all_pred_ddg_dict = {}

    k_ddg = []
    p_ddg = []

    for rec_corr in list_rec_corr_names:
        print rec_corr
        rec_corr_list = read_csv_list(rec_corr)
        #no known ddg
        if len(rec_corr_list[0]) == 3:
            continue
        amber_dg_dict = {}
        rosetta_dg_dict = {}
        
        #read in all amber csvs that correspond to column 3 in rec_corr file and rosetta ones too
        for record_id, prefix, filename, known_ddg, pred_ddg in rec_corr_list:
            amber_dg_dict[filename] = { "Mean Binding Energy" : get_mean_csv(os.path.join(amber_csv_path,filename+".csv"), protocol="amber"),
                                         "Bottom 3 Binding Energy" : get_bottom3_csv(os.path.join(amber_csv_path,filename+".csv"), protocol="amber"),
                                         "Mean Interaction Energy" : get_mean_txt(os.path.join(amber_inter_mean_path,filename+".txt")) }
            rosetta_dg_dict[filename] = { "Mean Binding Energy" : get_mean_csv(os.path.join(rosetta_csv_path,filename+".csv"), protocol="rosetta"), 
                                         "Bottom 3 Binding Energy" : get_bottom3_csv(os.path.join(rosetta_csv_path,filename+".csv"), protocol="rosetta"), 
                                         "Mean Interaction Energy" : get_mean_txt(os.path.join(rosetta_inter_mean_path,filename+".txt")),
                                         "Bottom 3 Interaction Energy" : get_bottom3_csv(os.path.join(rosetta_inter_path,filename+".csv")) }
    
        #find wt csv that correspond to wt row in rec_corr_file (column 2)
        wt_csv_name = [ rec[2] for rec in rec_corr_list if "wt" in rec[1] ][0]

        amber_ddg_dict = {}
        rosetta_ddg_dict = {}
        known_ddg_dict = {}
        pred_ddg_dict = {}
 
        #loops thru other records in rec_corr_dict
        for rec, prefix, filename, k,p in rec_corr_list:
            if "wt" not in prefix:
                if amber_ddg_dict.get(filename) is None:
                    amber_ddg_dict[filename] = {}
                if rosetta_ddg_dict.get(filename) is None:
                    rosetta_ddg_dict[filename] = {}
                for key, dg in amber_dg_dict[wt_csv_name].items():
                    amber_ddg_dict[filename][key] = amber_dg_dict[filename][key] - dg
                for key, dg in rosetta_dg_dict[wt_csv_name].items():
                    rosetta_ddg_dict[filename][key] = rosetta_dg_dict[filename][key] - dg
                known_ddg_dict[filename] = { "Known" : float(k) }
                pred_ddg_dict[filename] = { "Pred" : float(p) }

        all_amber_ddg_dict.update(amber_ddg_dict)
        all_rosetta_ddg_dict.update(rosetta_ddg_dict)
        all_known_ddg_dict.update(known_ddg_dict)
        all_pred_ddg_dict.update(pred_ddg_dict)        
   
        fig, axarr = conv.create_ax(max([len(d) for k, d in amber_dg_dict.items() ]+[len(d) for k,d in rosetta_dg_dict.items()]), 3, shx=True, shy=True)
        plot_ddg_dict(rosetta_ddg_dict,known_ddg_dict,axarr,0,"Rosetta",corr_values_dict)
        plot_ddg_dict(amber_ddg_dict,known_ddg_dict,axarr,1,"Amber",corr_values_dict)
        plot_ddg_dict(pred_ddg_dict,known_ddg_dict,axarr,2,"Pred",corr_values_dict)
       
        conv.save_fig(fig, out_csv_path + "/" + os.path.splitext(os.path.basename(rec_corr))[0] + ".txt", "ddg", max([len(d) for k, d in amber_dg_dict.items() ]+[len(d) for k,d in rosetta_dg_dict.items()])*4, 12)
 

    #Plot all correlation values
    
    fig_all, axarr_all = conv.create_ax(len(corr_values_dict["Rosetta"]),3)

    #assumes that Rosetta has more protocols than Amber
    for x_ind,(protocol, vals) in enumerate(corr_values_dict["Rosetta"].items()):
        if corr_values_dict["Amber"].get(protocol) is not None:
            amber_vals = corr_values_dict["Amber"][protocol]
        else:
            amber_vals = None
        pred_vals = corr_values_dict["Pred"]["Pred"]
        labels=["-PCC","-Rho","-Mae"]
        for ind,(val_list,label) in enumerate(zip(vals,labels)):
            series = [[val_list,pred_vals[ind],"Rosetta "+protocol]]
            if amber_vals is not None:
                series.append([amber_vals[ind],pred_vals[ind],"Amber "+protocol])
            scatterplot.plot_series(axarr_all[ind,x_ind], series, protocol,"Pred",label,colors=['coral','cyan'], size=40)
            scatterplot.add_x_y_line(axarr_all[ind,x_ind])

 	    #if x_ind == 2:   
 	    #    axarr_all[x_ind,y_ind].set_xlim([-0.2,10.0])
        #        axarr_all[x_ind,y_ind].set_ylim([-0.2,10.0])
    	#    	scatterplot.add_x_y_line(axarr_all[x_ind,y_ind],0.0,10.0)
	    #else:
		#axarr_all[x_ind,y_ind].set_xlim([-1.2,1.2])
        #        axarr_all[x_ind,y_ind].set_ylim([-1.2,1.2])
        #        scatterplot.add_x_y_line(axarr_all[x_ind,y_ind],-1.0,1.0)
	    
    conv.save_fig(fig_all, out_csv_path + "/all.txt", "ddg", 16, 12)

    fig_all_corr, axarr_all_corr = conv.create_ax(max([len(d) for k, d in all_amber_ddg_dict.items() ]+[len(d) for k,d in all_rosetta_ddg_dict.items()]), 3, shx=True, shy=True)
    plot_ddg_dict(all_rosetta_ddg_dict,all_known_ddg_dict,axarr_all_corr,0,"Rosetta",corr_values_dict)
    plot_ddg_dict(all_amber_ddg_dict,all_known_ddg_dict,axarr_all_corr,1,"Amber",corr_values_dict)
    plot_ddg_dict(all_pred_ddg_dict,all_known_ddg_dict,axarr_all_corr,2,"Pred",corr_values_dict)
    
    conv.save_fig(fig_all_corr, out_csv_path + "/all_corr.txt", "ddg",max([len(d) for k, d in amber_dg_dict.items() ]+[len(d) for k,d in rosetta_dg_dict.items()])*4, 12) 
        

def plot_ddg_dict(ddg_dict,known_ddg_dict,axarr,row,y_axis_name, corr_values_dict):
    total_dict = {}

    for filename, protocol_dict in ddg_dict.items():
        for title, ddg in protocol_dict.items():
            if total_dict.get(title) is None:
                total_dict[title] = [[],[]]
            total_dict[title][0].append(ddg)
            total_dict[title][1].append(known_ddg_dict[filename]["Known"])
    
    for ind, (title, (pred_ddg,known_ddg)) in enumerate(total_dict.items()):
        vals = draw_plot(axarr[row,ind], known_ddg, pred_ddg, 'b', title, "Known DDG", y_axis_name)

        #corr_values_dict has the following shape - "Pred" : { "Pred" : [ddg_vals] }, "Amber" : { "Mean.." : [ddg_vals], "Bott.." : [ddg_vals]}, "Rosetta" : { "Mean.." : [ddg_vals], "Bott.." : [ddg_vals]}     
        if corr_values_dict.get(y_axis_name) is None:
            corr_values_dict[y_axis_name] = {}
        if corr_values_dict[y_axis_name].get(title) is None:
            corr_values_dict[y_axis_name][title] = [[],[],[]]
        corr_values_dict[y_axis_name][title][0].append(vals[0])
        corr_values_dict[y_axis_name][title][1].append(vals[1])
        corr_values_dict[y_axis_name][title][2].append(vals[2])

def mean_abs_error(known, pred):
    sum_err=0.0
    for k,p in zip(known, pred):
        sum_err += np.abs(k-p)
    return sum_err/len(known)   

def draw_plot(ax, x, y, color, x_axis, y_axis, title):
    scatterplot.draw_actual_plot(ax, x, y, color, x_axis, y_axis, title, size=40)
    coeff, pval = pearsonr(x, y)
    rho, pval = spearmanr(x, y)
    mae = mean_abs_error(x, y)
    conv.add_text_dict(ax, { "PCC" : coeff, "Rho" : rho, "MAE" : mae })
        
    scatterplot.add_x_y_line(ax, min_val=min(x), max_val=max(x))

    return [coeff, rho, mae]

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument ('--rec_corr', help="record correspondence file")
    parser.add_argument ('--ddg_path', help="dg files")
    parser.add_argument ('--amber_pdb_path', help="In path for Amber pdbs")
    parser.add_argument ('--rosetta_pdb_path', help="In path for Rosetta pdbs")
    parser.add_argument ('--out_csv_path', help="Out path for final csv files")
    parser.add_argument ('--out_pdb_path', help="Out path for final pdb files")

    args = parser.parse_args()

    main(args.rec_corr, args.ddg_path, args.amber_pdb_path, args.rosetta_pdb_path, args.out_csv_path) 
