import numpy as np
import os
import pandas.core.algorithms as algos
import sys
from collections import Counter
from display import *
from math import sqrt, log, isnan, pow
from numpy import median
from scipy.interpolate import interp1d

""" Data Analysis Functions """
def get_min( data ):
	return min(data)

def get_max( data ):
	return max(data)

def get_median( data ):
	return median(data)

def get_mean( data ):
	return sum(data) / float(len(data))

def get_std_dev( data ):
	arr = np.array(data)
	return np.std(arr)

""" Data Parse Functions """
# Helps to remove zeros to prevent log error
def fix_zero_error(X):
	return [ 1 if x == 0 else x for x in X]

def data_not_flat(X):
	X_min = get_min(X)
	X_max = get_max(X)
	X_mean = get_mean(X)
	if X_mean == 0:
		X_div = get_std_dev(X)
	else:
		X_div = X_mean
	if X_div == 0:
		return False
	if ( float(X_max - X_min) / X_div ) <= 0.05:
		return False
	else:
		return True

# Returns quantile values for a list - 10% intervals
def quantile(x):
	vals = x.values
	return algos.quantile(vals, np.linspace(0,1,11))

# Returns mean of a group
def mean(x):
	vals = x.values
	return np.sum(vals[:-1]) / vals[:-1].size

# Returns variance of a group
def variance(x):
	vals = x.values
	return np.var(vals[:-1])


def generate_pairs(keys):
	pairs = []
	size = len(keys)
	for i in range(0, size):
		for j in range(0, size):
			if j > i:
				pairs.append( (keys[i], keys[j]) )
	return pairs

def combine_features(features):
	# Obtain Ids and check if all ids match
	ids = features[0].get_ids()
	for feature in features[1:]:
		if ids != feature.get_ids():
			print_fail("Ids dont match between features: " + feature.get_name() + " and " + feature[0].get_name())
			sys.exit()
	data = [ np.log(feature.get_data()) if feature.get_log() else np.array(feature.get_data()) for feature in features ]
	data = np.asarray(data, dtype = float)
	return ids, data.transpose()

def scale(x, P_val):
	return pow(float(1 + P_val*x), float(1 / P_val))

def scaling_function(rank_list, P_val):
	scores = [score[1] for score in rank_list]
	new_scores = [float("{0:.2f}".format(scale(score, P_val))) for score in scores]
	return np.matrix([[rank_list[i][0], new_scores[i]] for i in range(len(rank_list))])
	return new_scores

def get_coverage(plots, N_val, normal_matrix):
	max_values = {}
	obs_values = {}
	for row in normal_matrix:
		for value in row:
			outlier = int(value[0])
			plot = int(value[1])
			score = value[2]
			if outlier not in max_values:
				max_values[outlier] = score
				obs_values[outlier] = 0.0
				if plot in plots:
					obs_values[outlier] = score
			else:
				if score > max_values[outlier]:
					max_values[outlier] = score
				if score > obs_values[outlier] and plot in plots:
					obs_values[outlier] = score
	max_coverage = 0.0
	total_coverage = 0.0
	for outlier in max_values.keys():
		max_coverage += max_values[outlier]
		total_coverage += obs_values[outlier]
	return float(total_coverage) / N_val, float(max_coverage) / N_val

def generate_frequency_list(plots, scaled_matrix):
	outlier_max_plot = {}
	for row in scaled_matrix:
		for value in row:
			outlier = int(value[0])
			plot = int(value[
				1])
			score = value[2]
			if outlier not in outlier_max_plot:
				outlier_max_plot[outlier] = [-1, 0.0, -1]
			outlier_max_plot[outlier][1] += score
			if plot in plots:
				if score > outlier_max_plot[outlier][2]:
					outlier_max_plot[outlier][0] = plot
					outlier_max_plot[outlier][2] = score
	min_val = float("inf")
	max_val = 0
	for outlier in outlier_max_plot.keys():
		score = outlier_max_plot[outlier][1]
		if score < min_val:
			min_val = score
		if score > max_val:
			max_val = score
	frequencies = {}
	for outlier in outlier_max_plot.keys():
		m = interp1d([min_val,max_val],[outlier_circle_size*0.75, outlier_circle_size])
		size = m(outlier_max_plot[outlier][1])
		frequencies[outlier] = [int(size), int(outlier_max_plot[outlier][0])]
	return frequencies

def realign(Vals, IDs, DEST_IDs):
	output = []
	for id in IDs:
		try:
			idx = DEST_IDs.index(id)
			output.append(Vals[idx])
		except:
			output.append(0)
	return output

def init_environment(args):
	cprint("Initializing Environment")
	file = args.datafolder + args.datafile
	if os.path.isfile( file ):
		print_ok( "Datafile \"" + file + "\" successfully found" )
	else:
		print_fail( "Datafile \"" + file + "\" was not found" )
		sys.exit(1)

	if not os.path.exists( args.logfolder ):
	    os.makedirs( args.logfolder )
	    print_ok( "Logfolder successfully created" )
	else:
		print_ok( "Logfolder already found" )

	if not os.path.exists( args.plotfolder ):
	    os.makedirs( args.plotfolder )
	    print_ok( "plotfolder successfully created" )
	else:
		print_ok( "plotfolder already found" )

	if args.merge_ranklists and args.generate_iForest:
		print_fail( "Both merge ranklists and iForests cannot be made active at the same time to generate global outlier list" )
		sys.exit(1)
	elif args.merge_ranklists:
		print_ok( "Merge Ranklists algorithm will be used to generate a global outlier list" )
	elif args.generate_iForest:
		print_ok( "iForests outlier detection algorithm will be used to generate a global outlier list" )
	else:
		print_ok( "The global outlier list has been specified by the user" ) 

	try:
		float(args.p_val)
	except ValueError as e:
		print_fail( "p_val specified is not a float value. Using default value 1.0" )
		args.p_val = 1.0