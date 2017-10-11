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

data = read_data() # from data_transform.py

""" Plot Generator Helper Data """
cprint("Generating Plot Helper Data")
enable_warnings()
users = data.groupby('SOURCE')
IDs = map(int, users.groups.keys())
destinations = data.groupby('DESTINATION')
print_ok("Plot Helpers Generated")

""" Scatter Plots """
scatter_plots = 0 # Count of the number of scatter plots generated
if scatter_show:
	cprint ("Generating Scatter Plots")
	enable_warnings()
	['AMOUNT', 'DEST', 'LIFE', 'IN_EDGE', 'AMT_VAR', 'IAT_VAR']
	AMOUNT = fix_zero_error(users['WEIGHT'].sum().values.tolist())
	DEST = fix_zero_error(users['DESTINATION'].nunique().values.tolist())
	LIFE = fix_zero_error(users['LIFETIME'].first().values.tolist())
	IN_EDGE = fix_zero_error(users['WEIGHT'].count().values.tolist())
	IAT_VAR = fix_zero_error(users['IAT_VAR'].first().values.tolist())

	feature_pairs = generate_pairs(continuous_features, continuous_features + discrete_features)

	pp = PdfPages(plotfolder + 'scatterplots.pdf')
	for i, features in enumerate(feature_pairs):	
		# Generate Plot
		Y = features[0]
		X = features[1]
		fig = scatter_plot(eval(X), eval(Y), IDs, discription[Y], discription[X], discription[Y] + ' vs ' + discription[X], compare_value[X])
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
	ranklist.generate_graph(P_val, N_val)
	print_ok("Graph File Generated")
	# Run plotSpot to get selected graphs
	for B in Budget:
		for algo in ["SpellOut", "TopK", "Random"]:
			if algo != "SpellOut"  and not baseline:
				continue
			
			count += 1
			cprint("\nIteration " + str(count), RED)
			print "N_val = ", N_val, " Budget = ", B, " ALGO = ", algo
			
			start_time = time.time()
			cprint ("Running PlotSpot Algorithm")
			plots = plotSpot(B, algo)
			generate_frequency_list(plots)
			print_ok("PlotSpot Complete")
			elapsed_time = time.time() - start_time

			cprint("Saving Plots")
			coverage = get_coverage(plots, N_val)
			print "\t-> Total Plots Generated = ",
			cprint(scatter_plots, OKBLUE)
			print "\t-> Total Plots Chosen = ",
			cprint(len(plots), OKBLUE)
			print "\t-> Coverage = ",
			cprint("{0:.2f} %".format(coverage*100), OKBLUE)

			# Save selected plots in pdf
			pp = PdfPages(plotfolder + 'selectedplots_' + str(N_val) + "_" + str(B) + "_" + algo + '.pdf')
			for plot in plots:
				fig = scatter_outliers(plot, IDs)
				pp.savefig(fig)
			pp.close()
			print_ok("Plots Saved")
			
			file.write("N_val " + str(N_val) + "\tBudget " + str(B) + "\tAlgo " + algo + "\tTime Taken = " + str(elapsed_time) + "\tCoverage = "+ str(coverage) + "%" + "\n")
file.close()
cprint("Finished")
