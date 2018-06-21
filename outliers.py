import numpy as np
import pandas as pd
from display import *
from helper import scaling_function, combine_features
from iForest import *

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

def calculate_outliers(args, features, rank_matrix):
	cprint("Calculating Outliers")
	print( "\t-> Scaling Outlier Scores" )
	if args.merge_ranklists:		
		print( "\t-> Merging Rank Lists" )
		rank_lists = [scaling_function(list, float(args.p_val) ) for list in rank_matrix]
		outliers = combine_lists(rank_lists)[-args.num_outliers:]
	elif args.generate_iForest:
		print( "\t-> Generating iForest Outliers" )
		ids, data = combine_features(features.values())
		scores = iForest(ids, data)
		outliers = forest_outliers(args.num_outliers, scores)
	else:
		outliers = global_outlier_list
	print_ok("Outliers Calculated")
	return outliers