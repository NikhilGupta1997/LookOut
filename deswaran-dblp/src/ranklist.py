import numpy as np
import pandas as pd
import glob
import os
import math
from itertools import groupby
from operator import itemgetter
from iForest import forest_outliers
from collections import Counter
from helper import update_progress, print_ok, print_fail
from system import *

def read_file(filename):
	return np.matrix([map(float, line.strip('\n').split('\t')) for line in open(filename)])

def read_outliers(filename):
	return [map(float, line.strip('\n').split('\t'))[0] for line in open(filename)]

def get_max_values(rank_list):
	return [max(list[:,1]).item() for list in rank_list]

def extract_plots(files):
	return [int(filter(str.isdigit, file)) for file in files]

def combine_lists(rank_list):
	users = {}
	no_users = rank_list[0].shape[0]
	no_plots = len(rank_list)
	for i in range(no_users):
		user = rank_list[0][i].item(0)
		users[user] = [i]
		for j in range(1, no_plots):
			users[user].append(np.where((rank_list[j][:, 0] == user).all(axis=1))[0].item(0))
		update_progress(i+1, no_users)
	score_list = []	
	for user in users.keys():
		score = 0.0
		for pos in users[user]:
			score +=  1 / float(60 + pos)
		score_list.append((user, score))
	return [x[0] for x in sorted(score_list, key=lambda t: t[1])]
			
def write_to_outputfile(list, plot):
	f = open(filefolder + outputfile, 'a')
	for val in list:
		f.write(str(int(val.item(0))) + '\t' + str(plot) + '\t' + str(val.item(1)) + '\n')
	f.close()

def quantile_cut(scores, max_score):
	score_list = [score.tolist()[0][0] for score in scores]
	bins = np.linspace(0, max_score, quantile_bins)
	new_scores = np.matrix([float(bin)/quantile_bins for bin in np.digitize(score_list, bins)])
	return new_scores.transpose()

def standardize(new_list, plot_values, index):
	if max_divide:
		new_list[:,1] /= plot_values[index]
	elif quantile_divide:
		scores = new_list[:,1]
		new_scores = quantile_cut(scores, plot_values[index])
		new_list[:,1] = new_scores
	return new_list

def round_off(new_list):
	scores = new_list[:,1]
	new_scores = np.matrix([float("{0:.2f}".format(float(score))) for score in scores]).transpose()
	new_list[:,1] = new_scores
	return new_list

def scale(x, P_val):
	return math.pow(float(1 + P_val*x), float(1 / P_val))

def scaling_function(rank_list, P_val):
	scores = rank_list[:,1]
	new_scores = np.matrix([float("{0:.2f}".format(scale(score, P_val))) for score in scores]).transpose()
	rank_list[:,1] = new_scores
	return rank_list

def calculate_outliers(N, P_val):
	print "\t-> Reading Rank List Files"
	files = glob.glob(filefolder + '*_ranks.txt')
	plot_ids = extract_plots(files)
	rank_lists = [scaling_function(read_file(file), P_val) for file in files]
	if merge_ranklists:		
		print "\t-> Merging Rank Lists"
		outliers = combine_lists(rank_lists)[-N:]
	elif generate_iForest:
		print "\t-> Generating iForest Outliers"
		outliers = forest_outliers(N)
	else:
		print_fail("Select an Outlier Choosing Algorithm")
	plot_max_values = get_max_values(rank_lists)
	return rank_lists, outliers, plot_max_values, plot_ids

def generate_frequency_list():
	f = open(filefolder + frequencyfile, 'w')	
	scores = read_file(filefolder + outputfile)
	dtype = [('Col1','int32'), ('Col2','float32'), ('Col3','float32')]
	df = pd.DataFrame(scores)
	grouped_df = df.groupby(0)
	weights = []
	for key, item in grouped_df:
		weights.append((key, item[2].sum()))
	max_element = max(weights, key=lambda x:x[1])
	min_element = min(weights, key=lambda x:x[1])
	for key, item in weights:
		item = 2*(item - min_element[1]*0.5) * blue_circle / max_element[1]
		f.write(str(int(key)) + '\t' + str(int(item)) + '\n')
	f.close()

def generate_graph(P_val):
	try:
		os.remove(filefolder + outputfile)
	except OSError:
		pass
	rank_lists, outliers, plot_values, plot_ids = calculate_outliers(N, P_val)
	print "\t-> Standardising Outlier Weights"
	for index, list in enumerate(rank_lists):
		if algo_oddball:
			list = standardize(list, plot_values, index)
		list = round_off(list)
		delete_rows = [i for i in range(list.shape[0]) if list[i].item(0) not in outliers]
		new_list = np.delete(list, delete_rows, axis = 0)
		write_to_outputfile(new_list, plot_ids[index])
	print "\t-> Generating Frequency list " + str(P_val)
	generate_frequency_list()
