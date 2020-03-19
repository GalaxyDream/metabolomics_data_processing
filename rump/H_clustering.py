#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Description : This code do hierarchical clustering for peak table output by MZmine-2.53, 
              peak table should firstly be processed by "add_stats.py" before input to this program
Copyright   : (c) LemasLab, 02/23/2020
Author      : Xinsong Du
License     : GNU GPL-v3.0 License
Maintainer  : xinsongdu@ufl.edu, manfiol@ufl.edu, djlemas@ufl.edu
Usage       : python H_clustering.py -i $input_peak_table
                                    -d $design_file_location
                                    -o $output_figure_location
                                    -m $only_use_identified_metabolites_or_not
                                    -bs $do_blank_subtraction_or_not'''

import os
import logging
import logging.handlers

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s]: %(levelname)s: %(message)s')

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
import copy
import csv
import seaborn as sns; sns.set(color_codes=True)

import warnings
warnings.filterwarnings('ignore')

def H_clustering(data_file, design_file, output_fig, only_matched, BS):

    # load design file
    design = pd.read_csv(design_file)

    group_names = list(set(design['group']))
    group_names.sort()
#    blank_group_name = "zero-blank"
    group1_name = group_names[0]
    group2_name = group_names[1]

    data = pd.read_csv(data_file)
    group1_columns = design[design.group == group1_name].sampleID.tolist()
    group2_columns = design[design.group == group2_name].sampleID.tolist()

    if BS == "1":
        only_group1 = data[(data.adjusted_p_value < 0.05) & (data[str(group1_name) + '_mean'] > data[str(group2_name) + '_mean'])]
        only_group2 = data[(data.adjusted_p_value < 0.05) & (data[str(group1_name) + '_mean'] < data[str(group2_name) + '_mean'])]
        both = data[data.adjusted_p_value >= 0.05]
    else:
        only_group1 = data[(data[str(group1_name) + "_zero"] == True) & (data[str(group2_name) + "_zero"] == False)]
        only_group2 = data[(data[str(group1_name) + "_zero"] == False) & (data[str(group2_name) + "_zero"] == True)]
        both = data[(data[str(group1_name) + "_zero"] == False) & (data[str(group2_name) + "_zero"] == False)]

    if only_matched == "1":
        data = data[data.ppm < 5]
    data_filtered = copy.deepcopy(data)
    n_rows = min(50, len(data_filtered[data_filtered.adjusted_p_value < 0.05]))
    data_filtered = data_filtered[data_filtered.adjusted_p_value < 0.05]
    data_filtered = data_filtered.sort_values(by = 'p_value').iloc[0:n_rows]
    data_filtered.index = data_filtered.label
    data_filtered = data_filtered[group1_columns + group2_columns]

    # rename for each milk section
    for i, group1_column in enumerate(group1_columns):
        data_filtered.rename(columns = {group1_column: group1_name + '_' + str(i)}, inplace = True)
    for i, group2_column in enumerate(group2_columns):
        data_filtered.rename(columns = {group2_column: group2_name + '_' + str(i)}, inplace = True)

    logger.info(data_filtered.head())

    if len(data_filtered) <= 2:
        logger.info("empty fig")
        plt.savefig(output_fig)
        exit()

    # Plots
    logger.info("generating plot")
    g = sns.clustermap(np.log2(data_filtered + 1), figsize = (10, 20), xticklabels=True, yticklabels=True, cmap = "seismic", cbar_kws={'label': 'log2(intension)'}, method = 'ward')
    logger.info("adjusting direction of words")
    plt.setp(g.ax_heatmap.get_yticklabels(), rotation=0)
    logger.info("saving figures")
    g.savefig(output_fig)

if __name__ == '__main__':

    logger.info('generating hierachical clustering plot...')

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input', help="define the location of input csv file;", default="data_pos_ph.csv", required = False)
    parser.add_argument(
        '-d', '--design', help="define the location of input design csv file;", default="pos_design.csv", dest = "design", required = False)
    parser.add_argument(
        '-o', '--output', help="define the location of output figure;", default="h_cluster_pos_withbg.png", required = False)
    parser.add_argument(
        '-m', '--only_matched', help="if only include matched metabolites;", default="0", dest = "only_matched", required = False)
    parser.add_argument(
        '-bs', '--blank_subtraction', help="whether use blank subtraction;", dest = "blank_subtraction", default="1", required = False)

    args = parser.parse_args()
    H_clustering(args.input, args.design, args.output, args.only_matched, args.blank_subtraction)

