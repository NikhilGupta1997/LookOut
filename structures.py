import sys
from bisect import bisect_left
from collections import defaultdict
from helper import print_fail

""" Definition of an Outlier """
class Outlier:
	def __init__( self, id ):
		self.max_weight = 0.0 # Initially the outlier has no influence
		self.chosen = False
		self.id = id			

	def get_id( self ): # Unique identifier of the plot
		return self.id

	def isChosen( self ): # Bool to check if the outlier appears as an outlier in any of the chosen plots
		return self.chosen

	def update_weight( self, weight ): # Total influence of the outlier in chosen set of plots
		self.max_weight = self.max_weight + float( weight ) # Add influence of outlier by latest chosen plot
		self.chosen = True
		return self.max_weight

""" Definition of Edge of Bipartite Graph """
class Edge:
	def __init__( self, outlier_id, plot_id, weight ):
		self.outlier = outlier_id
		self.plot = plot_id
		self.weight = float( weight )
		self.max_weight = float( weight )

	def get_outlier( self ): # The Outlier assciated with the edge
		return self.outlier

	def get_plot( self ): # The Plot associated with the edge
		return self.plot

	def get_weight( self ): # The current weight of the edge (influence of outlier in corresponding plot)
		return self.weight

	def update_weight( self, weight ):
		self.weight = self.max_weight - float( weight )
		if self.weight <= 0.0:
			self.weight = 0.0
			return True
		else:
			return False

	def update_max_weight( self, max_weight ): # Used to normalize the max_weight of the outlier among plots
		self.weight = max_weight
		self.max_weight = max_weight

""" Definition of Plot """
class Plot:
	def __init__( self, id ):
		self.id = id
		self.value = 0.0

	def get_id( self ): # Unique identifier of the plot
		return self.id

	def get_value( self ): # Total influence of the plot
		return self.value

	def update_value( self, value ):
		self.value = value

class Graph:
	def __init__( self, bipartite_info ):
		self.outliers = {}
		self.plots = {}
		self.plot_table = []
		self.adjacency_list_plots = defaultdict(list)
		self.adjacency_list_outliers = defaultdict(list)
		self.edges = {}
		self.construct_graph(bipartite_info)

	def get_edge( self, outlier_id, plot_id ):
		return self.edges[ plot_id ][ outlier_id ]

	def get_plot( self, plot_id ):
		return self.plots[ plot_id ]

	def get_outlier( self, outlier_id ):
		return self.outliers[ outlier_id ]

	def insert_plot( self, plot ):
		self.plots[ plot.get_id() ] = plot

	def insert_outlier(self, outlier):
		self.outliers[ outlier.get_id() ] = outlier

	def insert_edge( self, edge ):
		if edge.get_plot() not in self.edges:
			self.edges[ edge.get_plot() ] = { }
		self.edges[ edge.get_plot() ][ edge.get_outlier() ] = edge
		self.adjacency_list_plots[ edge.get_plot() ].append( edge.get_outlier() )
		self.adjacency_list_outliers[ edge.get_outlier() ].append( edge.get_plot() )

	def remove_edge( self, edge ):
		del self.edges[ edge.get_plot() ][ edge.get_outlier() ]
		self.adjacency_list_plots[ edge.get_plot() ].remove( edge.get_outlier() )
		self.adjacency_list_outliers[ edge.get_outlier() ].remove( edge.get_plot() )

	# Returns the outliers connected to a plot
	def get_outlier_list( self, plot_id ):
		return self.adjacency_list_plots[ plot_id ]

	# Returns the plots connected to a outlier
	def get_plots_list( self, outlier_id ):
		return self.adjacency_list_outliers[ outlier_id ]

	# Calculates the score that a plot will add to the current overall score
	def calculate_plot_score( self,  plot_id ):
		outlier_list = self.get_outlier_list( plot_id )
		plot_score  = 0.0		
		for outlier_id in outlier_list:
			edge_weight = self.edges[ plot_id ][ outlier_id ].get_weight()
			plot_score =  plot_score + float( edge_weight )
		return plot_score

	# Update weights based after removing chosen plot
	def update_graph( self, plot_id ):
		outlier_list = self.get_outlier_list( plot_id )
		outlist = list(outlier_list)
		# Change edge weights based on outliers covered
		for outlier_id in outlist:
			edge_weight = self.edges[ plot_id ][ outlier_id ].get_weight()
			outlier_weight = self.outliers[ outlier_id ].update_weight( edge_weight )
			plots_list = self.get_plots_list( outlier_id )
			for plot_id_new in plots_list:
				edge = self.edges[ plot_id_new ][ outlier_id ]
				edge.update_weight( outlier_weight )
	
	# Helps to insert a plot-score tuple in sorted position in plot table
	def insert_plot_tuple( self, plot_tuple ):
		scores = [ x[1] for x in self.plot_table ]
		index = bisect_left( scores, plot_tuple[1] )
		self.plot_table.insert( index, plot_tuple )

	# Initializes the sorted plot table with plot_id and score tuples
	def construct_plot_table( self ):
		for plot_id in self.plots.keys():
			score = self.calculate_plot_score( plot_id )
			plot_tuple = ( plot_id, score )
			self.plot_table.append( plot_tuple )
		self.plot_table.sort( key = lambda x: x[1] )

	# Obtain the best plot from the plot table using lazy greedy algorithm
	def get_best_plot( self ):
		best_plot = self.plot_table.pop() # Top of the stack 
		new_score = self.calculate_plot_score( best_plot[0] )
		# Take advantage of submodularity here
		if new_score > best_plot[1]:
			print_fail( "SUBMODULATRITY ERROR. Stopping..." )
			sys.exit()
		if new_score >= self.plot_table[-1][1]: # Compare with score of next best element in stack
			return best_plot[0]
		else:
			self.insert_plot_tuple( (best_plot[0], new_score) ) # Maintain sorted stack
			return self.get_best_plot()

	# Ranks the plots initially for greedy selection (BASELINE)
	def get_plot_ranks( self ):
		ranks = []
		for plot_id in self.plots.keys():
			score = self.calculate_plot_score( plot_id ) # Score of each plot calculated independently of other plots
			ranks.append( (plot_id, score) )
		return [ int( plot ) for plot, score in sorted( ranks, key=lambda x:x[1], reverse=True ) ]

	# Sets the sum of edges of an outlier to 1
	def normalize_edges( self ):
		for outlier in self.outliers.keys():
			sum = 0.0
			plot_list = self.get_plots_list( outlier )
			for plot_id in plot_list:
				edge = self.get_edge( outlier, plot_id )
				sum += edge.max_weight
			for plot_id in plot_list:
				edge = self.get_edge( outlier, plot_id )
				edge.update_max_weight( float( edge.max_weight / sum ) )

	# Create Bi-partite Graph
	def construct_graph( self, bipartite_info ):
		print( "\t-> Constructing Graph" )
		for list in bipartite_info:	
			for values in list:
				# Create nodes and edges
				new_outlier = Outlier( values[0] )
				new_plot = Plot( values[1] )
				new_edge = Edge( values[0], values[1], values[2] )
				# Insert into Graph
				self.insert_outlier( new_outlier )
				self.insert_plot( new_plot ) 
				self.insert_edge( new_edge )
		# Create a ranked plot list which scores each plot
		print( "\t-> Constructing Plot Table" )
		self.construct_plot_table()