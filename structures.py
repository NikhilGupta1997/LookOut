from bisect import bisect_left
from collections import defaultdict

class Outlier:
	
	def __init__(self, id):
		self.max_weight = 0.0
		self.chosen = False
		self.id = id			

	def get_id(self):
		return self.id

	def isChosen(self):	
		return self.chosen

	def update_weight(self, weight):
		self.max_weight = self.max_weight + float( weight )
		self.chosen = True
		return self.max_weight

class Edge:

	def __init__(self, outlier_id, plot_id, weight):
		self.outlier = outlier_id
		self.plot = plot_id
		self.weight = float( weight )
		self.max_weight = float( weight )

	def get_outlier(self):
		return self.outlier

	def get_plot(self):
		return self.plot

	def get_weight(self):
		return self.weight

	def update_weight(self, weight):
		self.weight = self.max_weight - float( weight )
		if self.weight <= 0.0:
			self.weight = 0.0
			return True
		else:
			return False

class Plot:

	def __init__(self, id):
		self.id = id
		self.value = 0.0

	def get_id(self):
		return self.id

	def get_value(self):
		return self.value

	def update_value(self, value):
		self.value = value

class Graph:
	def __init__( self ):
		self.outliers = { }
		self.plots = { }
		self.plot_table = [ ]
		self.adjacency_list_plots = defaultdict(list)
		self.adjacency_list_outliers = defaultdict(list)
		self.edges = { }

	def print_covered( self ):
		for key in self.outliers:
			print self.outliers[key].get_id( ), " -> ", self.outliers[key].isChosen( )

	def get_edge( self, outlier_id, plot_id ):
		return self.edges[ plot_id ][ outlier_id ]

	def get_plot( self, plot_id ):
		return self.plots[ plot_id ]

	def get_outlier( self, outlier_id ):
		return self.outliers[ outlier_id ]

	def insert_plot( self, plot ):
		self.plots[ plot.get_id( ) ] = plot

	def insert_outlier(self, outlier):
		self.outliers[ outlier.get_id( ) ] = outlier

	def insert_edge( self, edge ):
		if edge.get_plot( ) not in self.edges:
			self.edges[ edge.get_plot( ) ] = { }
		self.edges[ edge.get_plot( ) ][ edge.get_outlier( ) ] = edge
		self.adjacency_list_plots[ edge.get_plot( ) ].append( edge.get_outlier( ) )
		self.adjacency_list_outliers[ edge.get_outlier( ) ].append( edge.get_plot( ) )

	def remove_edge( self, edge ):
		del self.edges[ edge.get_plot( ) ][ edge.get_outlier( ) ]
		self.adjacency_list_plots[ edge.get_plot( ) ].remove( edge.get_outlier( ) )
		self.adjacency_list_outliers[ edge.get_outlier( ) ].remove( edge.get_plot( ) )

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
			edge_weight = self.edges[ plot_id ][ outlier_id ].get_weight( )
			plot_score =  plot_score + float( edge_weight )
		return plot_score

	# Update weights based after removing chosen plot
	def update_graph( self, plot_id ):
		outlier_list = self.get_outlier_list( plot_id )
		outlist = list(outlier_list)
		# Change edge weights based on outliers covered
		for outlier_id in outlist:
			edge_weight = self.edges[ plot_id ][ outlier_id ].get_weight( )
			outlier_weight = self.outliers[ outlier_id ].update_weight( edge_weight )
			plots_list = self.get_plots_list( outlier_id )
			for plot_id_new in plots_list:
				edge = self.edges[ plot_id_new ][ outlier_id ]
				edge.update_weight( outlier_weight )
					#self.remove_edge( edge )
	
	# Helps to insert a plot-score tuple in sorted position in plot table
	def insert_plot_tuple( self, plot_tuple ):
		scores = [ x[1] for x in self.plot_table ]
		index = bisect_left( scores, plot_tuple[1] )
		self.plot_table.insert( index, plot_tuple )

	# Initializes the sorted plot table with plot_id and score tuples
	def construct_plot_table( self ):
		for plot_id in self.plots.keys( ):
			score = self.calculate_plot_score( plot_id )
			plot_tuple = ( plot_id, score )
			self.plot_table.append( plot_tuple )
		self.plot_table.sort( key = lambda x: x[1] )

	# Obtain the best plot from the plot table using lazy greedy algorithm
	def get_best_plot( self ):
		best_plot = self.plot_table.pop()
		new_score = self.calculate_plot_score( best_plot[0] )
		# Take advantage of submodularity here
		if new_score > best_plot[1]:
			print "SUBMODULATRITY ERROR"
		if new_score >= self.plot_table[-1][1]:
			return best_plot[0]
		else:
			self.insert_plot_tuple( (best_plot[0], new_score) )
			return self.get_best_plot()

	# Checks if *ALL* the outliers have been covered or not
	def is_covered( self ):
		for key in self.outliers:
			if not self.outliers[key].isChosen( ):
				return False
		return True

