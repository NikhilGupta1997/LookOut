from __future__ import print_function

import numpy as np
import oddball
import pandas.core.algorithms as algos
import sys
from collections import Counter
from math import sqrt, log, isnan, pow
from scipy.interpolate import interp1d
from system import *

# Returns bottom 5 percentile value in list
def get_bottom5(X):
	index = int(0.05*len(X))
	return sorted(X)[index]

# Returns top 5 percentile value in list
def get_top5(X):
	index = int(0.95*len(X))
	return sorted(X)[index]

# Median of a list
def get_median(X):
	return np.median(X)

# Geometric mean between 2 numbers
def geometric_mean(a, b):
	return sqrt(a*b)

# Helps to remove zeros to prevent log error
def fix_zero_error(X):
	return [ 1 if x == 0 else x for x in X]

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

# Calculates the log variance error of a line w.r.t. its band plot
def logvar(X, mid, low, high):
	var = 0.0
	for i in range(0,10):
		val = X['QUANTILE_' + str(i*10)].max()
		if val < low[i] or val > high[i]:
			var += 2*log(max(abs(val - mid[i]),1))
		else:
			var += log(max(abs(val - mid[i]),1))	
	return var

# Map the MCC indexes between two lists
def get_MCC_indexes(X1, X2):
	intersect = list(set(X1) & set(X2))
	ind1 = [X1.index(x) for x in intersect]
	ind2 = [X2.index(x) for x in intersect]
	return list(zip(ind1, ind2))

# Generate X values (MCC codes)
def generate_X(X, indexes):
	return [X[i] for i,_ in indexes]

# Generate Y values (Difference between list values)
def generate_Y(Y1, Y2, indexes):
	return [Y1[i] - Y2[j] for i,j in indexes]

def parametric_min(X, num):
	counts = sorted(Counter(X).items())
	for i in range(len(counts)):
		if counts[i][1] >= num:
			return counts[i][0]
	return None

def parametric_max(X, num):
	counts = sorted(Counter(X).items(), reverse=True)
	for i in range(len(counts)):
		if counts[i][1] >= num:
			return counts[i][0]
	return None

def enable_warnings():
	sys.stdout.write(WARNING)
	print( "..." )

def disable_warnings():
	sys.stdout.write(RESET)

def start_color(color):
	sys.stdout.write(color)

def end_color():
	sys.stdout.write(RESET)

def print_ok(text):
	end_color()
	print( "[ ", end='' )
	start_color(OKGREEN)
	print( "OK", end='' )
	end_color()
	print( " ] ", end='' )
	print( text )

def print_fail(text):
	end_color()
	print( "[ ", end='' )
	start_color(FAIL)
	print( "FAIL", end='' )
	end_color()
	print( " ] ", end='' )
	print( text )

def cprint(text, color=CYAN, end=None):
	if color == CYAN:
		print()
	start_color(color)
	print(text, end=end)
	end_color()

def update_progress(current, max):
	progress = float(current) / max
	barLength = 10
	block = int(round(barLength*progress))
	text = "\rPercent: [{0}] {1:.2f}%".format( "#"*block + "-"*(barLength - block) , progress*100)
	sys.stdout.write(text)
	sys.stdout.flush()
	if progress == 1:
		sys.stdout.write("\r")

def get_total_plots(A, B, C, D, E):
	total = 0
	if scatter_show:
		total += A
	if ccdf_show:
		total += B
	if hist_show:
		total += C
	if time_series_show:
		total += D
	if band_show:
		total += E
	return total

def generate_pairs(list1, list2):
	pairs = []
	for i, x in enumerate(list1):
		for j, y in enumerate(list2):
			if x != y and j >= i:
				pairs.append((x, y))
	return pairs

def combine_features(features):
	arr = np.asarray(features, dtype = float)
	arr[:, :] = np.log(arr[:, :])
	return arr.transpose()

def parse_cmdline():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--p_val", dest="p_val",
                      default = -0.8,
                      help="outlier scoring parameter")

    parser.add_option("--budget", dest="budget",
                      default = 5,
                      help = "budget of plots")
    (options, args) = parser.parse_args()
    return float(options.p_val), int(options.budget)

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
		m = interp1d([min_val,max_val],[blue_circle*0.75, blue_circle])
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
