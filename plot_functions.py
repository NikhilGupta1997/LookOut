import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
from collections import defaultdict
from helper import *
from iForest import iForest
from math import log10, ceil, isnan
from matplotlib.backends.backend_pdf import PdfPages
from system import *

SIZES = {
'title': 36,
'label': 36,
'tick': 28,
'annotation': 30,
'flag': 400
}

""" Scatter Plot Functions """
def generate_scatter_plots(args, features):
	cprint ("Generating Scatter Plots")
	feature_pairs = generate_pairs(features.keys())
	pp = PdfPages(args.plotfolder + 'scatterplots.pdf')
	plot_dict = {}
	rank_matrix = []
	for i, pair in enumerate(feature_pairs):	
		fig, rank_list = scatter_plot(features[pair[0]], features[pair[1]], args.output_plots) # Generate Plot
		rank_matrix.append(rank_list)
		plot_dict[i] = pair
		if args.output_plots:
			pp.savefig(fig)
		plt.close(fig)
		update_progress(i+1, len(feature_pairs))
	pp.close()
	print_ok('Scatter Plots Generated')
	return rank_matrix, plot_dict

def scatter_plot(feature_X, feature_Y, make_plot=False):
	ids, data = combine_features([feature_X, feature_Y])
	scores = iForest(ids, data)
	
	fig = plt.figure()
	if make_plot:
		X = feature_X.get_data()
		Y = feature_Y.get_data()
		ax = fig.add_subplot(111)
		ax.set_xlabel(feature_X.get_description(), fontsize=SIZES['label'])
		ax.set_ylabel(feature_Y.get_description(), fontsize=SIZES['label'])
		ax.xaxis.set_tick_params(labelsize=SIZES['tick'])
		ax.yaxis.set_tick_params(labelsize=SIZES['tick'])
		plt.gcf().subplots_adjust(bottom=0.18, left=0.18)
		plt.ylim([min(Y)/2.0, ceil(max(Y)*2.0)])
		plt.xlim([min(X)/2.0, ceil(max(X)*2.0)])
		plt.loglog(X, Y, 'k.')
	return fig, scores

# Find Outliers and frquency for plot
def scatter_outliers(feature_X, feature_Y, frequencies, plot):
	X_data = feature_X.get_data()
	Y_data = feature_Y.get_data()
	ids = feature_X.get_ids()
	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	ax1.set_xlabel(feature_X.get_description(), fontsize=SIZES['label'])
	ax1.set_ylabel(feature_Y.get_description(), fontsize=SIZES['label'])
	ax1.xaxis.set_tick_params(labelsize=SIZES['tick'])
	ax1.yaxis.set_tick_params(labelsize=SIZES['tick'])
	ax1.set_yscale('log')
	ax1.set_xscale('log')
	plt.ylim([min(Y_data)/2.0, ceil(max(Y_data)*2.0)])
	plt.xlim([min (X_data)/2.0, ceil(max(X_data)*2.0)])
	plt.gcf().subplots_adjust(bottom=0.18, left=0.18)
	ax1.scatter(X_data, Y_data, c = 'black', s = 50)
	for outlier in frequencies.keys():
		index = ids.index(outlier)
		size = frequencies[outlier][0]*10
		if plot == frequencies[outlier][1]:
			plt.scatter(X_data[index],Y_data[index], c = outlier_color[1], edgecolor='red', linewidth='1', s = int(size), alpha = 0.75)
		else:
			plt.scatter(X_data[index],Y_data[index], c = outlier_color[0], edgecolor='blue', linewidth='1', s = int(size), alpha = 0.75)
	return fig
