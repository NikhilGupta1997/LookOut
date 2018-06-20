import pandas as pd
import sys
from data import Feature
from helper import *

def read_data(args):
	print "Filename = ",
	cprint(args.datafile, OKGREEN)
	
	# Read data from csv file
	cprint("Reading File")
	data = pd.read_csv(args.datafolder + args.datafile, delimiter=args.data_delimiter) # Be patient, takes some time
	disable_warnings()
	print_ok("File Read Complete")

	""" TRANSFORMATIONS """
	cprint("Transformations")

	# Remove unwanted rows
	print "	-> Removing Unwanted Rows"
	data = data[data.groupby('SOURCE').SOURCE.transform(len)>=10] # Remove the entries with less than 10 transactions

	# Add User Lifetime Detail Columns
	print "	-> Calculating Lifetimes"
	data.insert(0,'FIRST_TRANSMISSION_DATE', data.groupby('SOURCE')['TIMESTAMP'].transform(lambda x: min(x)))
	data.insert(1,'LAST_TRANSMISSION_DATE', data.groupby('SOURCE')['TIMESTAMP'].transform(lambda x: max(x)))
	data['LIFETIME'] = (data['LAST_TRANSMISSION_DATE'] - data['FIRST_TRANSMISSION_DATE']) # Add column for user lifetime
	data = data[data.LIFETIME > 0]

	# Add IAT information
	print "	-> Adding IAT Information"
	data = data.sort_values(['SOURCE','TIMESTAMP'])
	data['NEXT_TIMESTAMP'] = data.groupby('SOURCE')['TIMESTAMP'].shift(-1)
	data['IAT'] = data['NEXT_TIMESTAMP'] - data['TIMESTAMP']
	data.insert(0,'MEAN_IAT', data.groupby('SOURCE')['IAT'].transform(lambda x: mean(x)))
	data.IAT.fillna(data.MEAN_IAT, inplace=True)
	# data.insert(1,'IAT_VAR', data.groupby('SOURCE')['IAT'].transform(lambda x: variance(x)))

	# Add Quantile information based on Amount Spent by the User
	print "	-> Adding IAT Quantile Information"
	users = data.groupby('SOURCE')
	update_progress(0, 11)
	quant_list = []
	for i in range(11):
		data.insert(i,'QUANTILE_' + str(10*i), users.IAT.transform(lambda x: quantile(x)[i]))
		quant_list.append('QUANTILE_' + str(10*i))
		update_progress(i+1, 11)
	data['IAT_VAR_MEAN']=data[quant_list].var(axis=1)
	data['MEDIAN_IAT']=data[quant_list[5]]
	print_ok("Transformations Complete")

	""" Plot Generator Helper Data """
	cprint("Generating Plot Helper Data")
	users = data.groupby('SOURCE')
	destinations = data.groupby('DESTINATION')
	print_ok("Plot Helpers Generated")

	SRC = fix_zero_error(destinations['SOURCE'].nunique().values.tolist())
	DEST = fix_zero_error(users['DESTINATION'].nunique().values.tolist())
	LIFE = fix_zero_error(users['LIFETIME'].first().values.tolist())
	EDGES_IN = fix_zero_error(destinations['WEIGHT'].count().values.tolist())
	EDGES_OUT = fix_zero_error(users['WEIGHT'].count().values.tolist())
	IAT_VAR_MEAN = fix_zero_error(users['IAT_VAR_MEAN'].first().values.tolist())
	MEAN_IAT = fix_zero_error(users['MEAN_IAT'].first().values.tolist())
	MEDIAN_IAT = fix_zero_error(users['MEDIAN_IAT'].first().values.tolist())
	IDs = [key for key, val in users['IAT_VAR_MEAN']]
	DEST_IDs = [key for key, val in destinations['SOURCE']]
	SRC = realign(SRC, IDs, DEST_IDs)
	EDGES_IN = realign(EDGES_IN, IDs, DEST_IDs)
	features = {}

	features['SRC'] = Feature('SRC', SRC, IDs)
	features['DEST'] = Feature('DEST', DEST, IDs)
	features['LIFE'] = Feature('LIFE', LIFE, IDs)
	features['EDGES_IN'] = Feature('EDGES_IN', EDGES_IN, IDs)
	features['EDGES_OUT'] = Feature('EDGES_OUT', EDGES_OUT, IDs)
	features['IAT_VAR_MEAN'] = Feature('IAT_VAR_MEAN', IAT_VAR_MEAN, IDs)
	features['MEAN_IAT'] = Feature('MEAN_IAT', MEAN_IAT, IDs)
	features['MEDIAN_IAT'] = Feature('MEDIAN_IAT', MEDIAN_IAT,IDs)
	features['EDGES_IN'] = Feature('EDGES_IN', EDGES_IN, IDs)

	return features
