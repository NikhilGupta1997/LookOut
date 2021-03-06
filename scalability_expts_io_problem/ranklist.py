import numpy as np
import pandas as pd
import glob
import os
import math
from scipy.interpolate import interp1d
from itertools import groupby
from operator import itemgetter
from iForest import forest_outliers
from collections import Counter
from helper import update_progress, print_ok, print_fail, scale, scaling_function
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

def calculate_outliers(N_val, P_val):
	# print "\t-> Reading Rank List Files"
	files = glob.glob(filefolder + '*_ranks.txt')
	rank_lists = [scaling_function(read_file(file), P_val) for file in files]
	plot_ids = extract_plots(files)
	if merge_ranklists:		
		# print "\t-> Merging Rank Lists"
		outliers = combine_lists(rank_lists)[-N_val:]
	elif generate_iForest:
		# print "\t-> Generating iForest Outliers"
		outliers = forest_outliers(N_val)
	else:
		print_fail("Select an Outlier Choosing Algorithm")
	plot_max_values = get_max_values(rank_lists)
	return rank_lists, outliers, plot_max_values, plot_ids

def generate_frequency_list(rank_lists, plot_ids, N_val):
	outlier_rank_list = [list[:N_val] for list in rank_lists]
	f = open(filefolder + frequencyfile, 'w')	
	scores = read_file(filefolder + outputfile)
	df = pd.DataFrame(scores)
	grouped_df = df.groupby(0)
	weights = []
	for key, item in grouped_df:
		sum = item[2].sum()
		item.get_value(item[2].argmax(), 1)
		plot_list = [plot_ids[i] for i, list in enumerate(outlier_rank_list) if key in list[:,0]]
		weights.append((key, sum, plot_list))
	max_element = max(weights, key=lambda x:x[1])
	min_element = min(weights, key=lambda x:x[1])
	for key, sum, plots in weights:
		m = interp1d([min_element[1],max_element[1]],[blue_circle/3, blue_circle])
		sum = m(sum)
		val = ' '.join([str(x) for x in plots])
		f.write(str(int(key)) + '\t' + str(int(sum)) + '\t' + val + '\n')
	f.close()

def generate_graph(P_val, N_val):
	try:
		os.remove(filefolder + outputfile)
	except OSError:
		pass
	rank_lists, outliers, plot_values, plot_ids = calculate_outliers(N_val, P_val)
	# print "\t-> Standardising Outlier Weights"
	for index, list in enumerate(rank_lists):
		if algo_oddball:
			list = standardize(list, plot_values, index)
		list = round_off(list)
		delete_rows = [i for i in range(list.shape[0]) if list[i].item(0) not in outliers]
		new_list = np.delete(list, delete_rows, axis = 0)
		write_to_outputfile(new_list, plot_ids[index])
	# print "\t-> Generating Frequency list " + str(P_val)
	generate_frequency_list(rank_lists, plot_ids, N_val)
