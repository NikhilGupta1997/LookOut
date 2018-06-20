from __future__ import print_function

import copy
import matplotlib.pyplot as plt
import time
from helper import *
from LookOut import LookOut
from plot_functions import scatter_outliers
from ranklist import generate_graph
from structures import Graph

""" Run algorithm to find best plots """
def run(args, features, rank_matrix, plot_dict, outlier_ids):
	# Quick Access Variables
	N_val = args.num_outliers
	B_val = args.budget
	P_val = float( args.p_val )

	# Create graph between outliers and plots
	cprint("Generating Bipartite Graph")
	scaled_matrix, normal_matrix = generate_graph(P_val, rank_matrix, outlier_ids)
	saved_graph = Graph(scaled_matrix)
	print_ok("Graph Generated Successfully")

	# Run appropriate algorithm to get list of selected graphs
	scatter_plots = len(plot_dict)
	file = open(args.logfolder + args.logfile, 'w')
	if args.baseline:
		algos = ["LookOut", "TopK", "Random"]
	else:
		algos = ["LookOut"]
	for algo in algos:
		cprint("\nIteration " + algo, RED)
		graph = copy.deepcopy(saved_graph)
		print( "N_val = ", N_val, " Budget = ", B_val )
		
		start_time = time.time()
		cprint( "Running " + algo + " Algorithm" )
		plots = LookOut(graph, B_val, algo)
		frequencies = generate_frequency_list(plots, scaled_matrix)
		print_ok(algo + " Complete")
		elapsed_time = time.time() - start_time

		cprint("Saving Plots")
		coverage, max_coverage = get_coverage(plots, N_val, normal_matrix)
		print( "\t-> Total Plots Generated = ", end='' ); cprint(scatter_plots, OKBLUE)
		print( "\t-> Total Plots Chosen = ", end='' ); cprint(len(plots), OKBLUE)
		print( "\t-> Coverage = ", end='' ); cprint("{0:.3f} / {1:.3f}".format(coverage, max_coverage), OKBLUE)

		# Save selected plots as png images
		for i, plot in enumerate(plots):
			pair = plot_dict[plot]
			fig = scatter_outliers(features[pair[0]], features[pair[1]], frequencies, plot)
			fname = args.plotfolder + '{0}-{1}-{2}-{3}.png'.format(algo, N_val, B_val, i)
			fig.savefig(fname)
			plt.close(fig)
		print_ok( "Plots Saved" )
		
		file.write("N_val " + str(N_val) + "\tBudget " + str(B_val) + "\tAlgo " + algo + "\tTime Taken = " + str(elapsed_time) + "\tCoverage = "+ str(coverage) + "%" + "\n")
	file.close()
	cprint( "Finished" )