import glob
import math
import numpy as np
import os
import pandas as pd
from collections import Counter
from helper import update_progress, print_ok, print_fail, scale, scaling_function
from iForest import forest_outliers
from itertools import groupby
from operator import itemgetter

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
			
def write_to_output(list, plot):
	return [[int(val.item(0)), plot, val.item(1)] for val in list]

def round_off(new_list):
	scores = new_list[:,1]
	new_scores = np.matrix([float("{0:.2f}".format(float(score))) for score in scores]).transpose()
	new_list[:,1] = new_scores
	return new_list

def calculate_outliers(args, N_val, rank_matrix):
	print "\t-> Reading Rank List Files"
	P_val = float(args.p_val)
	rank_lists = [scaling_function(list, P_val) for list in rank_matrix]
	cover_lists = [np.matrix(list) for list in rank_matrix]
	plot_ids = range(1, len(rank_lists) + 1)
	if args.merge_ranklists:		
		print "\t-> Merging Rank Lists"
		outliers = combine_lists(rank_lists)[-N_val:]
	elif args.generate_iForest:
		print "\t-> Generating iForest Outliers"
		outliers = forest_outliers(N_val)
	else:
		outliers = global_outlier_list
	return rank_lists, cover_lists, outliers, plot_ids

def generate_graph(args, N_val, rank_matrix):
	rank_lists, cover_lists, outliers, plot_ids = calculate_outliers(args, N_val, rank_matrix)
	print "\t-> Standardising Outlier Weights"
	scaled_matrix, normal_matrix = [], []
	for index, list in enumerate(rank_lists):
		delete_rows = [i for i in range(list.shape[0]) if list[i].item(0) not in outliers]
		new_list = round_off(np.delete(list, delete_rows, axis = 0))
		scaled_matrix.append(write_to_output(new_list, plot_ids[index]))
	for index, list in enumerate(cover_lists):
		delete_rows = [i for i in range(list.shape[0]) if list[i].item(0) not in outliers]
		new_list = round_off(np.delete(list, delete_rows, axis = 0))
		normal_matrix.append(write_to_output(new_list, plot_ids[index]))
	return scaled_matrix, normal_matrix
