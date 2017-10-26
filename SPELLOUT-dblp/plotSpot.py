from system import *
from structures import *
from helper import cprint
import random

""" Read the input file and construct a graph """
def construct_graph(scaled_matrix):
	print "\t-> Reading File"
	plot_graph = Graph( )
	print "\t-> Constructing Graph"
	for list in scaled_matrix:	
		for values in list:
			# Create nodes and edges
			new_outlier = Outlier( values[0] )
			new_plot = Plot( values[1] )
			new_edge = Edge( values[0], values[1], values[2] )
			# Insert into Graph
			plot_graph.insert_outlier( new_outlier )
			plot_graph.insert_plot( new_plot ) 
			plot_graph.insert_edge( new_edge )
	# Create a ranked plot list which scores each plot
	print "\t-> Constructing Plot Table"
	plot_graph.construct_plot_table( )
	return plot_graph

""" This will run the PlotSPOT algorithm to select the best plot cover """
def best_plots( graph, Budget ):
	best_plot_list = [ ]
	# Continue choosing plots till all the outliers are covered
	while Budget > 0:
		# Choose the next best plot which mazimizes score
		plot = graph.get_best_plot( )
		print "\t\t-> Choosen Plot is ", 
		cprint(plot, OKBLUE)
		best_plot_list.append(int( plot) )
		# Update the graph after removing chosen plot
		graph.update_graph( plot )
		Budget -= 1
	# Return a list of the chosen plots
	return best_plot_list

""" BASELINES """
def best_greedy( graph, Budget ):			# Baseline 1
	return graph.get_plot_ranks()[:Budget]

def random_plots( graph, Budget ):		# Baseline 2
	plots = graph.get_plot_ranks()
	return random.sample(plots, Budget)


def plotSpot( Budget, scaled_matrix, algo="SpellOut"):
	# Read the input file and construct the graph
	plot_graph = construct_graph(scaled_matrix)
	print "\t-> Choosing best plots"
	# Perform the PlotSPOT algorithm	
	if algo == "SpellOut":
		return best_plots( plot_graph, Budget )
	elif algo == "TopK":
		return best_greedy( plot_graph, Budget )
	else:
		return random_plots( plot_graph, Budget )
