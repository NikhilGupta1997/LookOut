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
repeat = 1

running_times = {}

# read file
data = pd.read_csv('Data/dblp_%d.txt' % num_edge, delimiter=' ')

s = time.time()
# transform
data = data_transform.read_data(data)
users = data.groupby('SOURCE')
IDs = map(int, users.groups.keys())
destinations = data.groupby('DESTINATION')

# extract features
AMOUNT = fix_zero_error(users['WEIGHT'].sum().values.tolist())
DEST = fix_zero_error(users['DESTINATION'].nunique().values.tolist())
LIFE = fix_zero_error(users['LIFETIME'].first().values.tolist())
IN_EDGE = fix_zero_error(users['WEIGHT'].count().values.tolist())
IAT_VAR = fix_zero_error(users['IAT_VAR'].first().values.tolist())

const = time.time()-s
print const
# run isolation forest in high dimensional space
features = combine_features([eval(F) for F in
        identity_features + continuous_features + discrete_features])
iForest(features)

# repeat experiments and average running time
for num_outlier in num_outliers:
    running_times[num_outlier] = []

    for t in range(repeat):

        # start clock

        ranklist.generate_graph(p_val, num_outlier)
        start_time = time.time()
        # select plot
        plots = plotSpot(budget, 'SpellOut')

        # end clock
        time_elapsed = time.time() - start_time + const
        running_times[num_outlier].append(time_elapsed)
        print num_outlier, t, time_elapsed

pickle.dump(running_times, open('results/scalability_outliers.pkl', 'wb'))
