import numpy as np
from helper import *
			
def write_to_output( list, plot ):
	return [ [ int(val.item(0)), plot, val.item(1) ] for val in list ]

def round_off(new_list):
	scores = new_list[:,1]
	new_scores = np.matrix( [ float( "{0:.2f}".format( float(score) ) ) for score in scores ] ).transpose()
	new_list[:,1] = new_scores
	return new_list

def get_matrix( P_val, rank_matrix ):
	rank_lists = [ scaling_function( list, P_val ) for list in rank_matrix ]
	cover_lists = [ np.matrix( list ) for list in rank_matrix ]
	return rank_lists, cover_lists

def generate_graph( P_val, rank_matrix, outliers ):
	rank_lists, cover_lists = get_matrix( P_val, rank_matrix )
	print( "\t-> Standardising Outlier Weights" )
	scaled_matrix, normal_matrix = [], []
	for index, list in enumerate( rank_lists ):
		delete_rows = [ i for i in range( list.shape[0] ) if list[i].item(0) not in outliers ]
		new_list = round_off( np.delete( list, delete_rows, axis = 0 ) )
		scaled_matrix.append( write_to_output( new_list, index ) )
	for index, list in enumerate( cover_lists ):
		delete_rows = [ i for i in range( list.shape[0] ) if list[i].item(0) not in outliers ]
		new_list = round_off( np.delete( list, delete_rows, axis = 0 ) )
		normal_matrix.append( write_to_output( new_list, index ) )
	return scaled_matrix, normal_matrix
