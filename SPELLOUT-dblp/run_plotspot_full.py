import ranklist
from plotSpot import plotSpot
from plot_functions import *
import cPickle as pickle
from sklearn.ensemble import IsolationForest
from matplotlib.backends.backend_pdf import PdfPages


num_outlier = 10
budget = 3

outlier_file_name = "top10_best"  # my personal best, containing Christos' name
# outlier_file_name = "top20" # all 20 features

features = []
if "best" in outlier_file_name:
    features = ['DEST', 'EDGES_OUT', 'LIFE', 'MEAN_IAT', 'IAT_VAR_MEAN',
                'IAT_q50']
else:
    features = ['DEST', 'EDGES_OUT', 'LIFE',
                'MEAN_IAT', 'IAT_VAR_MEAN', 'IAT_MIN', 'IAT_MAX',
                ] + ["IAT_q%d" % q for q in range(10, 91, 10)]


print 'loading'
INFO = pickle.load(open('results/info.pkl', 'rb'))
outliers = pickle.load(open('results/%s.pkl' % outlier_file_name, 'rb'))[:num_outlier]
global_outlier_list = outliers
# print 'outlier id to name mapping'
# author_id_to_name = {}
# with open('ent.dblp_coauthor') as f:
#     for line in f:
#         tokens = line.strip().replace('\"', '').split(' ')
#         author_id_to_name[int(tokens[0])] = tokens[1]
# print outliers
# print [author_id_to_name[INFO['IDs'][i]] for i in outliers]


# score from pair plots
feature_pairs = generate_pairs(features, features)
print feature_pairs
rank_matrix = []

outlier_ids = [INFO['IDs'].index(i) for i in outliers]

pp = PdfPages(plotfolder + 'scatterplots--full.pdf')
for j, features in enumerate(feature_pairs):
    X, Y = features[0], features[1]
    print j, 'of', len(feature_pairs)
    pair_features = np.array([INFO[features[0]], INFO[features[1]]]).T
    forest = IsolationForest(
        n_estimators=500, max_samples=1000,
        random_state=0, contamination=num_outlier / 343546.0 # number of nodes
    )
    fig = scatter_plot(INFO[X], INFO[Y], INFO['IDs'], discription[Y],
                                  discription[X],
                                  discription[Y] + ' vs ' + discription[X],
                                  compare_value[X])
    forest.fit(pair_features)
    scores = forest.decision_function(pair_features[outlier_ids, :])
    rank_list = sorted([(outliers[i], -s) for (i, s) in enumerate(scores)],
                       key=lambda x: x[1], reverse=True)
    rank_matrix.append(rank_list)
pp.close()


#  runs, properly till this, why is generate_graph returning nothing?
scaled_matrix, normal_matrix = ranklist.generate_graph(P_val, num_outlier, rank_matrix)
plots = plotSpot(budget, scaled_matrix, "SpellOut")
frequencies = generate_frequency_list(plots, scaled_matrix)
for i, plot in enumerate(plots):
    fig = scatter_outliers(plot, INFO['IDs'], frequencies)
    fname = 'discoveries/DBLP--full-{0}-{1}-{2}.png'.format(num_outlier,
                                                          budget, i)
    fig.savefig(fname)
