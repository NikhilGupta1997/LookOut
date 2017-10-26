import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import datetime as dt
import ranklist
import time
from plotSpot import plotSpot
from data_transform import read_data
from matplotlib.backends.backend_pdf import PdfPages
from math import log
from helper import *
from system import *
from plot_functions import *
from iForest import *
import cPickle as pickle
from sklearn.ensemble import IsolationForest


datafile = 'dblp_100000.txt'
continuous_features = ['DEST', 'EDGES_OUT', 'LIFE',
					   'MEAN_IAT', 'IAT_VAR_MEAN', 'IAT_q50']


data = read_data()
cprint("Generating Plot Helper Data")
enable_warnings()
users = data.groupby('SOURCE')
destinations = data.groupby('DESTINATION')
print_ok("Plot Helpers Generated")

INFO = {}

# INFO['SRC'] = fix_zero_error(destinations['SOURCE'].nunique().values.tolist())
INFO['DEST'] = fix_zero_error(users['DESTINATION'].nunique().values.tolist())
INFO['LIFE'] = fix_zero_error(users['LIFETIME'].first().values.tolist())
# INFO['EDGES_IN'] = fix_zero_error(destinations['WEIGHT'].count(
# ).values.tolist())
INFO['EDGES_OUT'] = fix_zero_error(users['WEIGHT'].count().values.tolist())
print 'till edges out'
INFO['IAT_VAR_MEAN'] = fix_zero_error(users['IAT_VAR_MEAN'].first().values.tolist())
INFO['MEAN_IAT'] = fix_zero_error(users['MEAN_IAT'].first().values.tolist())
# INFO['IAT_MIN'] = fix_zero_error(users['IAT_MIN'].first().values.tolist())
# INFO['IAT_MAX'] = fix_zero_error(users['IAT_MAX'].first().values.tolist())
# INFO['IAT_q10'] = fix_zero_error(users['QUANTILE_10'].first().values.tolist())
# INFO['IAT_q20'] = fix_zero_error(users['QUANTILE_20'].first().values.tolist())
# INFO['IAT_q30'] = fix_zero_error(users['QUANTILE_30'].first().values.tolist())
# INFO['IAT_q40'] = fix_zero_error(users['QUANTILE_40'].first().values.tolist())
INFO['IAT_q50'] = fix_zero_error(users['QUANTILE_50'].first().values.tolist())
# INFO['IAT_q60'] = fix_zero_error(users['QUANTILE_60'].first().values.tolist())
# INFO['IAT_q70'] = fix_zero_error(users['QUANTILE_70'].first().values.tolist())
# INFO['IAT_q80'] = fix_zero_error(users['QUANTILE_80'].first().values.tolist())
# INFO['IAT_q90'] = fix_zero_error(users['QUANTILE_90'].first().values.tolist())
print 'till iat'
INFO['IDs'] = [key for key, val in users['IAT_VAR_MEAN']]
# INFO['DEST_IDs'] = [key for key, val in destinations['SOURCE']]
print 'before realign'# following two lines are damn expensive
# INFO['SRC']= realign(INFO['SRC'], INFO['IDs'], INFO['DEST_IDs'])
# INFO['EDGES_IN'] = realign(INFO['EDGES_IN'], INFO['IDs'], INFO['DEST_IDs'])

print 'Info to file'
pickle.dump(INFO, open('results/info-sample.pkl', 'wb'))

print 'Constructing iForest'
few_features = combine_features([INFO[F] for F in continuous_features])

print ' nodes', len(INFO['IDs'])

num_outlier = 10
seed = 0
forest = IsolationForest(n_estimators=500, max_samples=512, random_state=seed,
                         contamination=num_outlier/float(len(INFO['IDs'])))
forest.fit(few_features)
prediction = forest.predict(few_features)
print [INFO['IDs'][i] for i in np.where(prediction == -1)[0]]

author_id_to_name = {}
with open('Data/ent.dblp_coauthor') as f:
    for line in f:
        tokens = line.strip().replace('\"', '').split(' ')
        author_id_to_name[int(tokens[0])] = tokens[1]
print sorted([author_id_to_name[INFO['IDs'][i]] for i in np.where(prediction == -1)[0]])
pickle.dump([INFO['IDs'][i] for i in np.where(prediction == -1)[0]],
            open('results/top%d-sample.pkl' % num_outlier, 'wb'))

