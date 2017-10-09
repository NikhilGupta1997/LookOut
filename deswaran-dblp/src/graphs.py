import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import datetime as dt
import ranklist
from plotSpot import plotSpot
from data_transform import read_data
from matplotlib.backends.backend_pdf import PdfPages
from math import log
from helper import *
from system import *
from plot_functions import *
from iForest import iForest

data = read_data() # from data_transform.py

""" Plot Generator Helper Data """
cprint("Generating Plot Helper Data")
enable_warnings()
users = data.groupby('ACCT_KEY')
IDs = map(int, users.groups.keys())
purchase_users = data[data['TRANSACTION_TYPE_CODE'] == 0].groupby('ACCT_KEY')
stores = data.groupby('MERCHANT_NAME_SCRUB')
days = data.groupby('DAYOFWEEK')
months = data.groupby('TIME_PERIOD')
hours = data.groupby('TRANSACTION_HOUR')
states = pd.DataFrame({'counts' : data.groupby('ACCT_KEY')['MERCHANT_STATE'].nunique()}).reset_index()
print_ok("Plot Helpers Generated")

""" Scatter Plots """
scatter_plots = 0 # Count of the number of scatter plots generated
if scatter_show:
	cprint ("Generating Scatter Plots")
	enable_warnings()
	AMOUNT = fix_zero_error(users['TRANSACTION_AMOUNT'].sum().values.tolist())
	TRANS = users['TRANSACTION_DATE'].count().values.tolist()
	PRCH_TRANS = fix_zero_error(users.TRANSACTION_TYPE_CODE.apply(lambda x: (x == 0).sum()).values.tolist())
	ACCT_TRANS = fix_zero_error(users.TRANSACTION_TYPE_CODE.apply(lambda x: (x != 0).sum()).values.tolist())
	LIFE = fix_zero_error(users['LIFETIME'].first().values.tolist())
	UNIQUE = users['MERCHANT_NAME_SCRUB'].nunique().values.tolist()
	MCC = fix_zero_error(users['MERCHANT_TRADE_CODE'].nunique().values.tolist())	
	STATES = fix_zero_error(users['MERCHANT_STATE'].nunique().values.tolist())

	feature_pairs = generate_pairs(continuous_features, continuous_features + discrete_features)

	pp = PdfPages(plotfolder + 'scatterplots.pdf')
	for i, features in enumerate(feature_pairs):	
		# Generate Plot
		Y = features[0]
		X = features[1]
		fig = scatter_plot(eval(X), eval(Y), IDs, discription[Y], discription[X], discription[Y] + ' vs ' + discription[X], compare_value[X])
		pp.savefig(fig)
		update_progress(i+1, len(feature_pairs))
	pp.close()
	scatter_plots = len(feature_pairs)
	print_ok('Scatter Plots Generated')

""" Generate CCDF Plots """
ccdf_plots = 0 # Count of the number of CCDF plots generated

""" Generate Histograms """
histograms = 0 # Count of the number of histogram plots generated

""" Generate Time Plots """
time_plots = 0 # Count of the number of time plots generated

""" Generate Band Plots """
band_plots = 0 # Count of the number of band plots generated

""" PlotSPOT Algorithm """
# Get Outliers Scores if using iForests
if generate_iForest:
	cprint("Generating Graph File")
	features = combine_features([eval(F) for F in identity_features + continuous_features + discrete_features])
	iForest(features)
	print_ok("iForest Generation Complete")
# Create graph between outliers and plots
cprint("Generating Graph File")
ranklist.generate_graph()
print_ok("Graph File Generated")
# Run plotSpot to get selected graphs
cprint ("Running PlotSpot Algorithm")
plots = plotSpot()
print_ok("PlotSpot Complete")
# Save selected plots in pdf
cprint("Saving Plots")
total_plots = get_total_plots(scatter_plots, ccdf_plots, histograms, time_plots, band_plots)
print "\t-> Total Plots Generated = ",
cprint(total_plots, OKBLUE)
print "\t-> Total Plots Chosen = ",
cprint(len(plots), OKBLUE)
print "\t-> Compression = ",
cprint("{0:.2f} %".format((1 - float(len(plots))/total_plots)*100), OKBLUE)
pp = PdfPages(plotfolder + 'selectedplots2.pdf')
for plot in plots:
	fig = scatter_outliers(plot, IDs)
	pp.savefig(fig)
pp.close()
print_ok("Plots Saved")
cprint("Finished")
