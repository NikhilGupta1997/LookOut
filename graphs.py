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
ccdf_plots = 7 # Count of the number of CCDF plots generated
if ccdf_show:
	cprint("Generating CCDF Plots")
	enable_warnings()
	pp = PdfPages(plotfolder + 'ccdfplots.pdf')
	## CCDF PLOT 1 ##
	#Amount Spend Per User
	CCDF1 = users['TRANSACTION_AMOUNT'].sum().values.tolist()
	fig = ccdf_plot(CCDF1, 'Amount Spent', 'Amount Spent per User')
	pp.savefig(fig)	
	update_progress(1, ccdf_plots)

	## CCDF PLOT 2 ##
	#Transactions per User
	CCDF2 = users['TRANSACTION_DATE'].count().values.tolist()
	fig = ccdf_plot(CCDF2, 'Number of Transactions', 'Transactions per User')
	pp.savefig(fig)
	update_progress(2, ccdf_plots)

	## CCDF PLOT 3 ##
	#Lifetime of User
	CCDF3 = users['LIFETIME'].mean().values.tolist()
	fig = ccdf_plot(CCDF3, 'Lifetime', 'Lifetime of User')
	pp.savefig(fig)
	update_progress(3, ccdf_plots)

	## CCDF PLOT 4 ##
	#Amount Spend Per Store
	CCDF4 = stores['TRANSACTION_AMOUNT'].sum().values.tolist()
	fig = ccdf_plot(CCDF4, 'Amount Spent', 'Amount Spent per Store')
	pp.savefig(fig)
	update_progress(4, ccdf_plots)

	## CCDF PLOT 5 ##
	#Transactions per Store
	CCDF5 = stores['TRANSACTION_DATE'].count().values.tolist()
	fig = ccdf_plot(CCDF5, 'Number of Transactions', 'Transactions per store')
	pp.savefig(fig)
	update_progress(5, ccdf_plots)

	## CCDF PLOT 6 ##
	#Lifetime of Store
	CCDF6 = stores['LIFETIME'].mean().values.tolist()
	fig = ccdf_plot(CCDF6, 'Lifetime', 'Lifetime per Store')
	pp.savefig(fig)
	update_progress(6, ccdf_plots)

	## CCDF PLOT 7 ##
	#Lifetime of Store
	CCDF7 = data['TRANSACTION_AMOUNT'].values.tolist()
	fig = ccdf_plot(CCDF7, 'Transaction Ammounts', 'Transaction Amounts')
	pp.savefig(fig)	
	update_progress(7, ccdf_plots)

	pp.close()
	print_ok("CCDF Plots Generated  ")

""" Generate Histograms """
histograms = 3 + 2*len(sorted(months.groups.keys())) - 1 # Count of the number of histogram plots generated
if hist_show:
	cprint("Generating Histogram Plots")
	enable_warnings()
	pp = PdfPages(plotfolder + 'histogramplots.pdf')
	## HISTOGRAM PLOT 1 ##
	#Amount Spend per Day over all users
	amounts = days['TRANSACTION_AMOUNT'].sum()
	HIST1_Y = amounts.values.tolist()
	HIST1_X = amounts.index.tolist()
	fig = hist_plot(HIST1_X, HIST1_Y, 'Days of the Week', 'Amount Spent', 'Amount Spent per Day of the Week')
	pp.savefig(fig)
	update_progress(1, histograms)

	## HISTOGRAM PLOT 2 ##
	#Number of transactions per Day of the week
	transactions = days['TRANSACTION_AMOUNT'].count()
	HIST2_Y = transactions.values.tolist()
	HIST2_X = transactions.index.tolist()
	fig = hist_plot(HIST2_X, HIST2_Y, 'Days of the Week', 'No. of Transactions', 'Transactions per Day of the Week')
	pp.savefig(fig)
	update_progress(2, histograms)

	## HISTOGRAM PLOT 3 ##
	#States per User
	HIST3_Y = [ x + 1 for x in states.groupby('counts')['ACCT_KEY'].count().values.tolist()]
	HIST3_X = states.groupby('counts')['ACCT_KEY'].count().index.tolist()
	fig = hist_plot(HIST3_X, HIST3_Y, 'No of States', 'No. of Users', 'States Visited per User')
	plt.yscale('log')
	pp.savefig(fig)
	update_progress(3, histograms)

	## HISTOGRAM PLOT 4 ##
	#Month Wise Analysis via MCC
	periods = sorted(months.groups.keys())
	for i in range(len(periods)):
		if (i+1) == len(periods):
			fig = hist_plot(CURR_X, CURR_Y, 'MCC Codes', 'Amount Spent', 'Period ' + str(periods[i]))
			plt.yscale('log')
			pp.savefig(fig)
			update_progress(4 + 2*i, histograms)
		else:		
			if i == 0:
				mcc_groups = data[data['TIME_PERIOD'] == periods[i]].groupby('MERCHANT_TRADE_CODE')
				mcc_amounts = mcc_groups['TRANSACTION_AMOUNT'].sum()
				LAST_Y = mcc_amounts.values.tolist()
				LAST_X = mcc_amounts.index.tolist()
			else:
				LAST_Y = CURR_Y
				LAST_X = CURR_X
			fig = hist_plot(LAST_X, LAST_Y, 'MCC Codes', 'Amount Spent', 'Period ' + str(periods[i]))
			plt.yscale('log')
			pp.savefig(fig)
			update_progress(4 + 2*i, histograms)
			mcc_groups = data[data['TIME_PERIOD'] == periods[i+1]].groupby('MERCHANT_TRADE_CODE')
			mcc_amounts = mcc_groups['TRANSACTION_AMOUNT'].sum()
			CURR_Y = mcc_amounts.values.tolist()
			CURR_X = mcc_amounts.index.tolist()
			fig = hist_compare(CURR_X, CURR_Y, LAST_X, LAST_Y, 'MCC Codes', 'Amount Difference', 'Difference ' + str(periods[i]) + ' and ' + str(periods[i+1]))
			#plt.yscale('log')
			pp.savefig(fig)
			update_progress(5 + 2*i, histograms)
	
	pp.close()	
	print_ok("Histograms Generated  ")

""" Generate Time Plots """
time_plots = 4 # Count of the number of time plots generated
if time_series_show:
	cprint("Generating Time Series Plots")
	enable_warnings()	
	pp = PdfPages(plotfolder + 'timeseries.pdf')
	## TIME SERIES PLOT 1 ##
	#Amount Spent Per Time Period
	amounts = months['TRANSACTION_AMOUNT'].sum()
	TS1_Y= amounts.values.tolist()
	TS1_X = amounts.index.tolist()
	TS1_X = [dt.datetime.strptime(date, '%Y-%m').date() for date in TS1_X]
	fig = time_plot(TS1_X, TS1_Y, 'Time Period', 'Amount Spent', 'Amount Spent per Time Period')
	pp.savefig(fig)
	update_progress(1, time_plots)

	## TIME SERIES PLOT 2 ##
	#Transactions Per Time Period
	transactions = months['TRANSACTION_AMOUNT'].count()
	TS2_Y = transactions.values.tolist()
	TS2_X = transactions.index.tolist()
	TS2_X = [dt.datetime.strptime(date, '%Y-%m').date() for date in TS2_X]
	fig = time_plot(TS2_X, TS2_Y, 'Time Period', 'Number of Transactions', 'Transactions per Time Period')
	pp.savefig(fig)
	update_progress(2, time_plots)

	## TIME SERIES PLOT 3 ##
	#Amount Spent Per Hour of the Day
	non_credit = data[data['TRANSACTION_DESCRIPTION'] != 'ACH Load Credit'].groupby('TRANSACTION_HOUR')
	amounts = non_credit['TRANSACTION_AMOUNT'].sum()	
	TS3_Y = amounts.values.tolist()
	TS3_X = amounts.index.tolist()
	fig = time_plot(TS3_X, TS3_Y, 'Hour of Day', 'Amount Spent', 'Amount Spent per Hour of Day', 0, 23)
	pp.savefig(fig)
	update_progress(3, time_plots)

	## TIME SERIES PLOT 4 ##
	#Transactions Per Hour of the Day
	non_credit = data[data['TRANSACTION_DESCRIPTION'] != 'ACH Load Credit'].groupby('TRANSACTION_HOUR')
	transactions = non_credit['TRANSACTION_AMOUNT'].count()
	TS4_Y = transactions.values.tolist()
	TS4_X = transactions.index.tolist()
	#TS4_X = [dt.datetime.strptime(str(date), '%H').date() for date in TS4_X]
	fig = time_plot(TS4_X, TS4_Y, 'Hour of Day', 'Number of Transactions', 'Transactions per Hour of Day', 0, 23)
	pp.savefig(fig)
	update_progress(4, time_plots)

	pp.close()
	print_ok("Time Plots Generated  ")

""" Generate Band Plots """
band_plots = 11 # Count of the number of band plots generated
if band_show:
	cprint("Generating Band Plots")
	enable_warnings()
	pp = PdfPages(plotfolder + 'bandplots.pdf')
	## BAND PLOT 1 ##
	#Amount Spend per User
	BAND1_Y = [get_median(users['QUANTILE_'+str(i*10)].first().values.tolist()) for i in range(0,10)]
	BAND1_Y_low = [get_bottom5(users['QUANTILE_'+str(i*10)].first().values.tolist()) for i in range(0,10)]
	BAND1_Y_high = [get_top5(users['QUANTILE_'+str(i*10)].first().values.tolist()) for i in range(0,10)]
	BAND1_X = np.linspace(0,100,10)
	fig = band_plot(BAND1_X, BAND1_Y, BAND1_Y_low,  BAND1_Y_high, 'Quantile', 'Amount Spent', 'Amount Spent per Quantile Analysis')
	pp.savefig(fig)
	update_progress(1, band_plots)

	## BAND PLOT 2 ##
	#Outlier w.r.t. band model
	logvars = users.apply(lambda x: logvar(x, BAND1_Y, BAND1_Y_low, BAND1_Y_high)).reset_index().set_index('ACCT_KEY')
	top10 = logvars.nlargest(10, 0).index.tolist()
	for num, out in enumerate(top10):
		BAND_OUT_Y = [users.get_group(out)['QUANTILE_'+str(i*10)].max() for i in range(0,10)]
		fig = band_plot_overlay(BAND1_X, BAND1_Y, BAND1_Y_low,  BAND1_Y_high, BAND_OUT_Y, 'Quantile', 'Amount Spent', 'Amount Spent per Quantile Analysis ' + str(out))
		pp.savefig(fig)
		update_progress(2 + num, band_plots)
	
	pp.close()
	print_ok("Band Plots Generated  ")

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
