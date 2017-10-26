import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import sys
import cPickle as pickle

SIZES = {
'title': 36,
'label': 36,
'tick': 28,
'annotation': 30,
'flag': 400
}


def log_fit_line(x, y, log=False):
    """ Fits line by logarithmic binning of x values
    Args:
        x (array-list) : 1d array of positive values
        y (array-list) : 1d array of positive values
    Returns:
        (dict) : dictionary of bin_avg, line's x and y, slope, corr values
    """
    if log:
        line = np.polyfit(np.log(x),np.log(y), 1)
        return {
        'm': line[0],
        'x': x,
        'y': np.exp(np.poly1d(line)(np.log(x))),
        'corr': scipy.stats.pearsonr(
        np.log(x), np.log(y)
        )[0]
        }
    else:
        line = np.polyfit(x, y, 1)
        return {
            'm': line[0],
            'x': x,
            'y': np.poly1d(line)(x),
            'corr': scipy.stats.pearsonr(
                x, y
            )[0]
        }


def plot(values, x_label, x, log=False):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    y = np.array([np.average(values[x_val]) for x_val in x])

    line = log_fit_line(x, y)
    # plot
    ax.scatter(x, y, color='k', marker='^', s=SIZES['flag'])
    ax.plot(line['x'], line['y'], color='k', linestyle='--', linewidth=4)
    # title, label, ticks, scale
    # ax.set_title(dataset_name.upper(), fontsize=SIZES['title'])
    ax.set_xlabel(x_label, fontsize=SIZES['label'])
    ax.set_ylabel('running time (s)', fontsize=SIZES['label'])
    if log:
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlim([0.6 * np.min(x), np.max(x) * 5])
        ax.set_ylim([0.6 * np.min(y), np.max(y) * 5])
    ax.xaxis.set_tick_params(labelsize=SIZES['tick']-2)
    ax.yaxis.set_tick_params(labelsize=SIZES['tick']-2)

    ax.text(0.95, 0.03, 'linear scaling',
            verticalalignment='bottom', horizontalalignment='right',
            transform=ax.transAxes, fontsize=SIZES['annotation'])
    print line['m']
    # save
    plt.gcf().subplots_adjust(bottom=0.18, left=0.18)
    fname = 'results/scalability-%s.png' % x_label.replace('number of ', '')
    fig.savefig(fname)
    plt.clf()


num_edges = np.power(10, range(3, 8))
num_outliers = range(10, 91, 10)

# edges_values = pickle.load(open('results/scalability_edges.pkl', 'rb'))
outlier_values = pickle.load(open('results/scalability_outliers.pkl', 'rb'))

# plot(edges_values, 'number of edges', num_edges, log=True)
plot(outlier_values, 'number of anomalies', num_outliers)
