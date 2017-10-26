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


def log_fit_line(x, y, nbins=20):
    """ Fits line by logarithmic binning of x values
    Args:
        x (array-list) : 1d array of positive values
        y (array-list) : 1d array of positive values
    Returns:
        (dict) : dictionary of bin_avg, line's x and y, slope, corr values
    """
    try:
        assert np.min(x) != np.max(x)
    except:
        'x is a constant, binning failed in log_fit_line()'
        sys.exit(1)
    # x_edges =  np.logspace(
    # base=2, start=np.log2(np.min(x)), stop=np.log2(np.max(x)), num=nbins+1
    # )
    # x_bins, y_bins = np.zeros(nbins), np.zeros(nbins)
    # for i in xrange(nbins):
    #     x_bins[i] = np.average(x_edges[i:i+2])
    #     y_bins[i] = np.average(y[np.logical_and(x>=x_edges[i], x<=x_edges[i+1])])
    # select_bins = y_bins>0
    line = np.polyfit(np.log(x),np.log(y), 1)
    return {
    'm': line[0],
    'x': x,
    'y': np.exp(np.poly1d(line)(np.log(x))),
    'corr': scipy.stats.pearsonr(
    np.log(x), np.log(y)
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
    ax.xaxis.set_tick_params(labelsize=SIZES['tick'])
    ax.yaxis.set_tick_params(labelsize=SIZES['tick'])
    # annotation
    # ax.legend()
    # ax.text(0.95, 0.15, 'corr: %1.2f' % line['corr'],
    #         verticalalignment='bottom', horizontalalignment='right',
    #         transform=ax.transAxes, fontsize=SIZES['annotation'])
    if log:
        ax.text(0.95, 0.03, r'slope $\approx$ 1.00',
                verticalalignment='bottom', horizontalalignment='right',
                transform=ax.transAxes, fontsize=SIZES['annotation'])
        # ax.text(0.95, 0.03, 'slope = %1.2f' % line['m'],
        #         verticalalignment='bottom', horizontalalignment='right',
        #         transform=ax.transAxes, fontsize=SIZES['annotation'])
    print line['m']
    # save
    plt.gcf().subplots_adjust(bottom=0.18, left=0.18)
    fname = 'results/scalability-%s.png' % x_label.replace('number of ', '')
    fig.savefig(fname)
    plt.clf()


num_edges = np.power(10, np.linspace(3, 6.5, 8)).astype(int)
num_outliers = np.array(range(10, 101, 10))

# edges_values = pickle.load(open('results/scalability_edges_1.pkl', 'rb'))
string = """316 0 0.0966980457306
1000 0 0.142249107361
3162 0 0.445537805557
10000 0 1.16844797134
31622 0 2.79598593712
100000 0 7.41218590736
316227 0 15.1371920109
1000000 0 48.4494519234
3162277 0 127.018903971"""
edges_values = {}
for line in string.split('\n'):
    tokens = line.split(' ')
    edges_values[int(tokens[0])] = [float(tokens[2])]
plot(edges_values, 'number of edges', num_edges, log=True)

# outlier_values = pickle.load(open('results/scalability_outliers.pkl', 'rb'))
# plot(outlier_values, 'number of outliers', num_outliers)
