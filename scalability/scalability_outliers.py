import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import datetime as dt
import ranklist
import time
from plotSpot import plotSpot
import data_transform
from matplotlib.backends.backend_pdf import PdfPages
from math import log
from helper import *
from system import *
import plot_functions
from iForest import iForest
import time
import copy
import cPickle as pickle


p_val, budget, num_edge = -0.8, 5, 10000

num_outliers = range(10, 91, 10)
repeat = 20

running_times = {}

# read file
data = pd.read_csv('Data/dblp_%d.txt' % num_edge, delimiter=' ')

# transform
data = data_transform.read_data(data)
users = data.groupby('SOURCE')
IDs = map(int, users.groups.keys())
destinations = data.groupby('DESTINATION')

AMOUNT = fix_zero_error(users['WEIGHT'].sum().values.tolist())
DEST = fix_zero_error(users['DESTINATION'].nunique().values.tolist())
LIFE = fix_zero_error(users['LIFETIME'].first().values.tolist())
IN_EDGE = fix_zero_error(users['WEIGHT'].count().values.tolist())
IAT_VAR = fix_zero_error(users['IAT_VAR'].first().values.tolist())

num_nodes = len(AMOUNT)

feature_pairs = generate_pairs(continuous_features,
                               continuous_features + discrete_features)

# repeat experiments and average running time
for num_outlier in num_outliers:
    running_times[num_outlier] = []

    for t in range(repeat):

        # score in 2d
        rank_matrix = []
        construction_time, scoring_time = 0., 0.
        for i, features in enumerate(feature_pairs):
            # Generate Plot
            Y = features[0]
            X = features[1]
            rank_list, con_time, scor_time = plot_functions.scatter_plot(
                eval(X), eval(Y), IDs, discription[Y], discription[X],
                discription[Y] + ' vs ' + discription[X], compare_value[X]
            ) # score all points in 2d
            rank_matrix.append(rank_list)
            construction_time += con_time
            scoring_time += scor_time

        features = combine_features([eval(F) for F in
                                     identity_features + continuous_features + discrete_features])
        iForest(features)

        start_time = time.time()
        scaled_matrix, normal_matrix = ranklist.generate_graph(P_val,
                                                       num_outlier, rank_matrix)
        # time_graph_gen = (time.time() - start_time) * num_outlier / (
        #     num_nodes - num_outlier)

        start_time = time.time()
        # select plots
        plots = plotSpot(budget, scaled_matrix, 'SpellOut')
        # frequencies = generate_frequency_list(plots, scaled_matrix)

        # end clock
        time_elapsed = (time.time() - start_time) + \
            construction_time + (scoring_time * num_outlier / num_nodes)
        running_times[num_outlier].append(time_elapsed)
        print num_outlier, t, time_elapsed

pickle.dump(running_times, open('results/scalability_outliers.pkl', 'wb'))
