import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import datetime as dt
import ranklist
import time
from plotSpot import plotSpot
from data_transform import read_data
from matplotlib.backends.backend_pdf import PdfPages
from math import log
from helper import *
from system import *
from plot_functions import *
from iForest import iForest

datafile = 'dblp_100000.txt'
continuous_features = ['DEST', 'EDGES_OUT', 'LIFE',
					   'MEAN_IAT', 'IAT_VAR_MEAN', 'IAT_q50']



data = read_data() # from data_transform.py




""" Plot Generator Helper Data """
cprint("Generating Plot Helper Data")
enable_warnings()
users = data.groupby('SOURCE')
destinations = data.groupby('DESTINATION')
print_ok("Plot Helpers Generated")

""" Scatter Plots """
rank_matrix = []
scatter_plots = 0 # Count of the number of scatter plots generated
if scatter_show:
	cprint ("Generating Scatter Plots")
	enable_warnings()
	['SRC', 'DEST', 'EDGES_IN', 'EDGES_OUT', 'LIFE', 'MEDIAN_IAT', 'MEAN_IAT', 'IAT_VAR_MEAN']
	SRC = fix_zero_error(destinations['SOURCE'].nunique().values.tolist())
	DEST = fix_zero_error(users['DESTINATION'].nunique().values.tolist())
	LIFE = fix_zero_error(users['LIFETIME'].first().values.tolist())
	EDGES_IN = fix_zero_error(destinations['WEIGHT'].count().values.tolist())
	EDGES_OUT = fix_zero_error(users['WEIGHT'].count().values.tolist())
	IAT_VAR_MEAN = fix_zero_error(users['IAT_VAR_MEAN'].first().values.tolist())
	MEAN_IAT = fix_zero_error(users['MEAN_IAT'].first().values.tolist())
	MEDIAN_IAT = fix_zero_error(users['MEDIAN_IAT'].first().values.tolist())
	IAT_q10 = fix_zero_error(users['QUANTILE_10'].first().values.tolist())
	IAT_q20 = fix_zero_error(users['QUANTILE_20'].first().values.tolist())
	IAT_q30 = fix_zero_error(users['QUANTILE_30'].first().values.tolist())
	IAT_q40 = fix_zero_error(users['QUANTILE_40'].first().values.tolist())
	IAT_q50 = fix_zero_error(users['QUANTILE_50'].first().values.tolist())
	IAT_q60 = fix_zero_error(users['QUANTILE_60'].first().values.tolist())
	IAT_q70 = fix_zero_error(users['QUANTILE_70'].first().values.tolist())
	IAT_q80 = fix_zero_error(users['QUANTILE_80'].first().values.tolist())
	IAT_q90 = fix_zero_error(users['QUANTILE_90'].first().values.tolist())
	IDs = [key for key, val in users['IAT_VAR_MEAN']]
	DEST_IDs = [key for key, val in destinations['SOURCE']]
	SRC = realign(SRC, IDs, DEST_IDs)
	EDGES_IN = realign(EDGES_IN, IDs, DEST_IDs)


	feature_pairs = generate_pairs(continuous_features, continuous_features + discrete_features)

	pp = PdfPages(plotfolder + 'scatterplots.pdf')
	for i, features in enumerate(feature_pairs):	
		# Generate Plot
		Y = features[0]
		X = features[1]
		fig, rank_list = scatter_plot(eval(X), eval(Y), IDs, discription[Y], discription[X], discription[Y] + ' vs ' + discription[X], compare_value[X])
		rank_matrix.append(rank_list)
		if output_plots:
			pp.savefig(fig)
		update_progress(i+1, len(feature_pairs))
	pp.close()
	scatter_plots = len(feature_pairs)
	print_ok('Scatter Plots Generated')

""" PlotSPOT Algorithm """
# Get Outliers Scores if using iForests
if generate_iForest:
	cprint("Generating Graph File")
	features = combine_features([eval(F) for F in identity_features + continuous_features + discrete_features])
	iForest(features)
	print_ok("iForest Generation Complete")

file = open(filefolder + logfile, 'w')

# Use outlier list if provided
if not generate_iForest and not merge_ranklists:
	N_list = [len(global_outlier_list)]

count = 0
for N_val in N_list:
	# Create graph between outliers and plots
	cprint("Generating Graph File")
	scaled_matrix, normal_matrix = ranklist.generate_graph(P_val, N_val, rank_matrix)
	print_ok("Graph File Generated")
	# Run plotSpot to get selected graphs
	for algo in ["SpellOut", "TopK"]:
		plot_coverage = []
		for B in Budget:
			if algo != "SpellOut"  and not baseline:
				continue
			
			count += 1
			cprint("\nIteration " + str(count), RED)
			print "N_val = ", N_val, " Budget = ", B, " ALGO = ", algo
			
			start_time = time.time()
			cprint ("Running PlotSpot Algorithm")
			plots = plotSpot(B, scaled_matrix, algo)
			frequencies = generate_frequency_list(plots, scaled_matrix)
			print_ok("PlotSpot Complete")
			elapsed_time = time.time() - start_time

			cprint("Saving Plots")
			coverage, max_coverage = get_coverage(plots, N_val, normal_matrix)
			plot_coverage.append("{0:.3f}".format(coverage))
			print "\t-> Total Plots Generated = ",
			cprint(scatter_plots, OKBLUE)
			print "\t-> Total Plots Chosen = ",
			cprint(len(plots), OKBLUE)
			print "\t-> Coverage = ",
			cprint("{0:.3f} / {1:.3f}".format(coverage, max_coverage), OKBLUE)

			if output_plots:
				# Save selected plots in pdf
				pp = PdfPages(plotfolder + 'selectedplots_' + str(N_val) + "_" + str(B) + "_" + algo + '.pdf')
				for i, plot in enumerate(plots):
					fig = scatter_outliers(plot, IDs, frequencies)
					fname = 'discoveries/LBNL-{0}-{1}-{2}.png'.format(N_val, B, i)
					fig.savefig(fname)
    				pp.savefig(fig)
				pp.close()
				print_ok("Plots Saved")
			
			file.write("N_val " + str(N_val) + "\tBudget " + str(B) + "\tAlgo " + algo + "\tTime Taken = " + str(elapsed_time) + "\tCoverage = "+ str(coverage) + "%" + "\n")
		print plot_coverage, max_coverage
file.close()
cprint("Finished")
