from __future__ import print_function

import random
from helper import cprint, print_fail
from structures import *
from system import *

""" BASELINES """
# Baseline 1
def best_greedy( graph, Budget ): # TopK
	return graph.get_plot_ranks()[:Budget]

# Baseline 2
def random_plots( graph, Budget ): # Random
	plots = graph.get_plot_ranks()
	return random.sample( plots, Budget )

""" LookOut Algorithm """
# Select the optimised plot cover
def best_plots( graph, Budget ):
	best_plot_list = []
	# Continue choosing plots till the budget is exhausted
	while Budget > 0:
		# Choose the next best plot which mazimizes score
		plot = graph.get_best_plot()
		best_plot_list.append( int( plot ) )
		# Update the graph after removing chosen plot
		graph.update_graph( plot )
		Budget -= 1
	# Return a list of the chosen plots
	return best_plot_list

# Optimized Algorithm
def LookOut( graph, budget, algo="LookOut" ):
	print( "\t-> Choosing best plots" )
	if algo == "LookOut":
		plots = best_plots( graph, budget )
	elif algo == "TopK":
		plots = best_greedy( graph, budget )
	elif algo == "Random":
		plots = random_plots( graph, budget )
	else:
		print_fail( "The Algorithm specified doesn't lie in { LookOut, TopK, Random }. Skipping ..." )
		return
	print( "\t\t-> Choosen Plots are ", end='') 
	cprint( str(plots), OKBLUE )
	return plots