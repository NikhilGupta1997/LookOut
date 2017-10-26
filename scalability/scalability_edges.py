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

p_val, budget, num_outlier = 1, 5, 50
num_edges = np.power(10, np.linspace(2.5, 7.5, 11)).astype(int)
repeat = 1

running_times = {}

for num_edge in num_edges:

    # read file
    raw_data = pd.read_csv('Data/dblp_%d.txt' % num_edge, delimiter=' ')

    # repeat experiments and average running time
    running_times[num_edge] = []
    for t in range(repeat):
        # start clock
        data = copy.deepcopy(raw_data)
        start_time = time.time()

        # feature extraction
        data = data_transform.read_data(data)
        users = data.groupby('SOURCE')
        IDs = map(int, users.groups.keys())
        destinations = data.groupby('DESTINATION')
        AMOUNT = fix_zero_error(users['WEIGHT'].sum().values.tolist())
        DEST = fix_zero_error(users['DESTINATION'].nunique().values.tolist())
        LIFE = fix_zero_error(users['LIFETIME'].first().values.tolist())
        IN_EDGE = fix_zero_error(users['WEIGHT'].count().values.tolist())
        IAT_VAR = fix_zero_error(users['IAT_VAR'].first().values.tolist())


        # get global list of outliers
        features = combine_features([eval(F) for F in
                                     identity_features + continuous_features + discrete_features])
        iForest(features)

        feature_pairs = generate_pairs(continuous_features,
                                   continuous_features + discrete_features)
        rank_matrix = []
        for i, features in enumerate(feature_pairs):
            # Generate Plot
            Y = features[0]
            X = features[1]
            rank_list = plot_functions.scatter_plot(
                eval(X), eval(Y), IDs, discription[Y], discription[X],
                discription[Y] + ' vs ' + discription[X], compare_value[X]
            )
            rank_matrix.append(rank_list)

        # select plots

        scaled_matrix, normal_matrix = ranklist.generate_graph(P_val,
                                                   num_outlier, rank_matrix)
        plots = plotSpot(budget, scaled_matrix, 'SpellOut')
        # frequencies = generate_frequency_list(plots, scaled_matrix)

        # end clock
        time_elapsed = time.time() - start_time
        running_times[num_edge].append(time_elapsed)
        print num_edge, t, time_elapsed

# print running_times
pickle.dump(running_times, open('results/scalability_edges_1.pkl', 'wb'))
