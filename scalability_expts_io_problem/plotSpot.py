from system import *
from structures import *
from helper import cprint
import time

""" Read the input file and construct a graph """
def construct_graph( ):
	f = open(filefolder + outputfile, 'r')
	# print "\t-> Reading File"
	plot_graph = Graph( )
	# print "\t-> Constructing Graph"
	for line in f:	
		values = line.strip('\n').split('\t')
		# Create nodes and edges
		new_outlier = Outlier( values[0] )
		new_plot = Plot( values[1] )
		new_edge = Edge( values[0], values[1], values[2] )
		# Insert into Graph
		plot_graph.insert_outlier( new_outlier )
		plot_graph.insert_plot( new_plot ) 
		plot_graph.insert_edge( new_edge )
	# Create a ranked plot list which scores each plot
	# print "\t-> Constructing Plot Table"
	plot_graph.construct_plot_table( )
	return plot_graph

""" This will run the PlotSPOT algorithm to select the best plot cover """
def best_plots( graph, Budget ):
	best_plot_list = [ ]
	# Continue choosing plots till all the outliers are covered
	while Budget > 0:
		# Choose the next best plot which mazimizes score
		plot = graph.get_best_plot( )
		# print "\t\t-> Choosen Plot is ",
		# cprint(plot, OKBLUE)
		best_plot_list.append(int( plot) )
		# Update the graph after removing chosen plot
		graph.update_graph( plot )
		Budget -= 1
	# Return a list of the chosen plots
	return best_plot_list

def best_greedy( graph, Budget):
	return graph.get_plot_ranks()[:Budget]

def best_greedy_norm( graph, Budget):
	graph.normalize_edges();
	return graph.get_plot_ranks()[:Budget]

["SpellOut", "Greedy", "Greedy_Norm"]
def plotSpot( Budget, algo="SpellOut" ):
	# Read the input file and construct the graph
	plot_graph = construct_graph( )
	# print "\t-> Choosing best plots"
	# Perform the PlotSPOT algorithm	
	if algo == "SpellOut":
		return best_plots( plot_graph, Budget )
	elif algo == "Greedy":
		return best_greedy( plot_graph, Budget )
	else:
		return best_greedy_norm( plot_graph, Budget )

