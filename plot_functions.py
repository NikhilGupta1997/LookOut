import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import oddball
from collections import defaultdict
from math import log10, ceil, isnan
from iForest import iForest
from system import *
from helper import *

plot_num = 0

""" Scatter Plot Functions """
def scatter_plot(X, Y, IDs, yname, xname, title, val):
	# Main Plot	
	global plot_num
	plot_num = plot_num + 1
	fig = plt.figure(plot_num)
	fig.text(0.5, 0.04, xname, ha = 'center')
	fig.text(0.04, 0.5, yname, va = 'center', rotation = 'vertical')
	ax1 = fig.add_subplot(211)
	plt.title(title)	
	plt.loglog(X, Y, 'k.')

	if algo_oddball:
		# Interpolate the median line
		minX = parametric_min(X, val); maxX = parametric_max(X, val)
		binedges = np.logspace(log10(minX), log10(maxX), 10)
		median_points_X = []; median_points_Y = []
		median_points_X.append(minX)
		median_points_Y.append(get_median([Y[j] for j in [ind for ind, x in enumerate(X) if x == minX]]))
		for i in xrange(1, 10):
			median_points_X.append(int(geometric_mean(binedges[i], binedges[i-1])))
			median_points_Y.append(get_median([Y[j] for j in [ind for ind, x in enumerate(np.digitize(X, binedges)) if x == i]]))
			if isnan(float(median_points_Y[-1])):
				median_points_Y.pop(); median_points_X.pop()
		median_points_X.append(maxX)
		median_points_Y.append(get_median([Y[j] for j in [ind for ind, x in enumerate(X) if x == maxX]]))
		plt.plot(median_points_X, median_points_Y, 'ro-')

		# Calculate Oddball Scores
		scores = oddball.get_scores(median_points_X, median_points_Y, X, Y, IDs)

	elif algo_iForests:
		features = combine_features([IDs, X, Y])	
		scores = iForest(features)
	else:
		print_fail("Scoring Algorithm not Chosen")

	# Write rank and scores to outputfile
	write_to_file(scores, plot_num)	

	# Heat Map
	heatmap, xedges ,yedges = np.histogram2d(X, Y, bins=(np.logspace(0, ceil(log10(max(X))), 400), np.logspace(0, ceil(log10(max(Y))), 250)))
	extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
	ax2 = fig.add_subplot(212, sharex = ax1, sharey = ax1)
	plt.xscale('log'); plt.yscale('log')
	cmap = plt.cm.jet
	cmap.set_under(color = 'white')
	plt.imshow(heatmap.T, extent = extent, origin='lower', aspect='auto', cmap = cmap, vmin = 0.01)
	return fig

# Outlier overlay on plot
def scatter_overlay(X, Y):
	plt.subplot(211)
	for i in range(len(X)):
		plt.loglog(X[i],Y[i], c = colors[i%5], marker = shapes[i/5], mew = 0.0, ms = 10)

# Find Outliers and frquency for plot
def scatter_outliers(plot, IDs):
	outliers = get_plot_outliers(plot)
	frequencies = get_outlier_frequencies()
	fig = plt.figure(plot)
	ax = fig.axes[0]
	line = ax.lines[0]
	X_data = line.get_xdata()
	Y_data = line.get_ydata()
	for outlier in outliers:
		index = IDs.index(outlier)
		plt.subplot(211)
		plt.loglog(X_data[index],Y_data[index], c = colors[0], marker = shapes[1], mew = 0.1, ms = (frequencies[outlier] + 6), alpha = 0.8)
	return fig

""" CCDF Plot Functions """
def ccdf_plot(X, xname, title):
	global plot_num
	plot_num = plot_num + 1
	counts, bin_edges = np.histogram(X, bins = np.logspace(0, log10(max(X)), 300))
	counts = np.insert(counts, 0, 0)
	cdf = counts.cumsum() / float(len(X))
	ccdf = [1-x for x in cdf]
	fig = plt.figure(plot_num)
	plt.xscale('log')
	plt.ylim([0,1])
	plt.ylabel('CCDF')
	plt.plot(bin_edges, ccdf)
	plt.title(title)
	plt.xlabel(xname)
	return fig

""" Histogram Plot Functions """
def hist_plot(X, Y, xname, yname, title):
	global plot_num
	plot_num = plot_num + 1
	fig = plt.figure(plot_num)	
	plt.bar(X, Y)
	plt.ylabel(yname)
	plt.xlabel(xname)
	plt.title(title)
	return fig

# Plots the positive values
def hist_pos(X, Y, xname, yname, title, llimit, ulimit):
	global plot_num
	plot_num = plot_num + 1
	fig = plt.figure(plot_num)	
	plt.bar(X, Y, color = 'g', edgecolor = 'g')
	plt.xlim([llimit, ulimit])
	plt.ylabel(yname)
	plt.xlabel(xname)
	plt.title(title)
	plt.yscale('log')
	return fig

# Plots the negative value overlays
def hist_neg(X, Y):
	plt.bar(X, Y, color='r', edgecolor = 'r')

# Creates a histogram of the difference between two histogram plots
def hist_compare(X1, Y1, X2, Y2, xname, yname, title):
	indexes = get_MCC_indexes(X1, X2)
	DIFF_X = generate_X(X1, indexes)
	DIFF_Y = generate_Y(Y1, Y2, indexes)
	lowerlimit = min(DIFF_X)
	upperlimit = max(DIFF_X)
	posx = []; posy = []; negx = []; negy = []
	for i, val in enumerate(DIFF_Y):
		if val >= 0:
			posx.append(DIFF_X[i])
			posy.append(val)
		else:
			negx.append(DIFF_X[i])
			negy.append(-1*val)
	fig = hist_pos(posx, posy, xname, yname, title, lowerlimit, upperlimit)
	hist_neg(negx, negy)
	return fig

""" Time Plot Functions """
def time_plot(X, Y, xname, yname, title, llimit = None, ulimit = None):
	global plot_num
	plot_num = plot_num + 1
	fig = plt.figure(plot_num)
	plt.plot(X, Y, 'b-o')
	plt.ylabel(yname)
	plt.xlabel(xname)
	plt.title(title)
	if ulimit != None:
		plt.xlim([llimit, ulimit])
	return fig

""" Band Plot Functions """
# Creates a Band Plot
def band_plot(X, Y1, Y2, Y3, xname, yname, title):
	global plot_num
	plot_num = plot_num + 1
	fig = plt.figure(plot_num)
	plt.plot(X, Y1, 'b-o')
	plt.plot(X, Y2, 'g-o')
	plt.plot(X, Y3, 'g-o')
	plt.fill_between(X, Y2, Y3, color='g', alpha=0.5)
	plt.ylabel(yname)
	plt.xlabel(xname)
	plt.title(title)
	plt.yscale('log')
	return fig

# Creates a Band Plot with a user value overlay
def band_plot_overlay(X, Y1, Y2, Y3, Y, xname, yname, title):
	fig = band_plot(X, Y1, Y2, Y3, xname, yname, title)
	plt.plot(X, Y, 'r-o')
	return fig

def show_plots(plots):
	for plot in plots:
		fig = plt.figure(plot)
		fig.show()

