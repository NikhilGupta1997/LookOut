import sys
import numpy as np
import pandas.core.algorithms as algos
import oddball
from scipy.interpolate import interp1d
from math import sqrt, log, isnan, pow
from collections import Counter
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

# Write to plot_outlier output file
def write_to_file(ranks, plot_num):
	f = open(filefolder + str(plot_num) + rankfile, 'w')	
	for rank, score in enumerate(ranks):
		f.write(str(score[0]) + '\t' + str(score[1]) + '\n') 
	f.close()

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
	print "..."

def disable_warnings():
	sys.stdout.write(RESET)

def start_color(color):
	sys.stdout.write(color)

def end_color():
	sys.stdout.write(RESET)

def print_ok(text):
	end_color()
	print "[ ",
	start_color(OKGREEN)
	print "OK",
	end_color()
	print " ]",
	print text

def print_fail(text):
	end_color()
	print "[ ",
	start_color(FAIL)
	print "FAIL",
	end_color()
	print " ]",
	print text

def cprint(text, color=CYAN):
	if color == CYAN:
		print
	start_color(color)
	print text
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

def get_plot_outliers(plot):
	outliers = []
	for row in open(filefolder + outputfile):
		value = row.strip('\n').split('\t')
		if int(value[1]) == plot:
			outliers.append(int(value[0]))
	return outliers

def get_outlier_frequencies():
	frequency = {}
	for row in open(filefolder + frequencyfile):
		values = row.strip('\n').split('\t')
		key = int(str(values[0])); size = int(values[1]); plot = [int(value) for value in values[2].split(' ')]
		frequency[key] = [size, plot]
	return frequency

def generate_pairs(list1, list2):
	pairs = []
	for i, x in enumerate(list1):
		for j, y in enumerate(list2):
			if x != y and j >= i:
				pairs.append((x, y))
	return pairs

def combine_features(features):
	arr = np.asarray(features, dtype = float)
	arr[1:, :] = np.log(arr[1:, :])
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
	scores = rank_list[:,1]
	new_scores = np.matrix([float("{0:.2f}".format(scale(score, P_val))) for score in scores]).transpose()
	rank_list[:,1] = new_scores
	return rank_list

def get_coverage(plots, N_val):
	obs_values = {}
	scores = np.matrix([map(float, line.strip('\n').split('\t')) for line in open(filefolder + coverfile, 'r')])
	for row in scores:
		outlier = int(row.item(0))
		plot = int(row.item(1))
		score = row.item(2)
		if outlier not in obs_values:
			obs_values[outlier] = 0.0
			if plot in plots:
				obs_values[outlier] = score
		else:
			if score > obs_values[outlier] and plot in plots:
				obs_values[outlier] = score
	total_coverage = 0.0
	for outlier in obs_values.keys():
		total_coverage += obs_values[outlier]
	return float(total_coverage) / N_val

# def get_coverage(plots, N_val):
# 	max_values = {}
# 	obs_values = {}
# 	scores = np.matrix([map(float, line.strip('\n').split('\t')) for line in open(filefolder + coverfile, 'r')])
# 	for row in scores:
# 		outlier = int(row.item(0))
# 		plot = int(row.item(1))
# 		score = row.item(2)
# 		if outlier not in max_values:
# 			max_values[outlier] = score
# 			obs_values[outlier] = 0.0
# 			if plot in plots:
# 				obs_values[outlier] = score
# 		else:
# 			if score > max_values[outlier]:
# 				max_values[outlier] = score
# 			if score > obs_values[outlier] and plot in plots:
# 				obs_values[outlier] = score
# 	max_coverage = 0.0
# 	total_coverage = 0.0
# 	for outlier in max_values.keys():
# 		max_coverage += max_values[outlier]
# 		total_coverage += obs_values[outlier]
# 	return float(total_coverage) / max_coverage

def generate_frequency_list(plots):
	outlier_max_plot = {}
	f = open(filefolder + frequencyfile, 'w')	
	scores = np.matrix([map(float, line.strip('\n').split('\t')) for line in open(filefolder + outputfile, 'r')])
	for row in scores:
		outlier = int(row.item(0))
		plot = int(row.item(1))
		score = row.item(2)
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
	for outlier in outlier_max_plot.keys():
		m = interp1d([min_val,max_val],[blue_circle/3, blue_circle])
		size = m(outlier_max_plot[outlier][1])
		f.write(str(int(outlier)) + '\t' + str(int(size)) + '\t' + str(int(outlier_max_plot[outlier][0])) + '\n')
	f.close()

