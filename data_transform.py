import pandas as pd
import sys
from helper import *
from system import *

def read_data():
	print "Filename = ",
	cprint(datafile, OKGREEN)
	
	# Read data from csv file
	cprint("Reading File")
	enable_warnings()
	data = pd.read_csv(datafolder + datafile, delimiter=data_delimiter) # Be patient, takes some time
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
	data.insert(1,'IAT_VAR', data.groupby('SOURCE')['IAT'].transform(lambda x: variance(x)))

	# # Add Quantile information based on Amount Spent by the User
	# print "	-> Adding IAT Quantile Information"
	# users = data.groupby('SOURCE')
	# update_progress(0, 11)
	# quant_list = []
	# for i in range(11):
	# 	data.insert(i,'QUANTILE_' + str(10*i), users.IAT.transform(lambda x: quantile(x)[i]))
	# 	quant_list.append('QUANTILE_' + str(10*i))
	# 	update_progress(i+1, 11)
	# data['IAT_VAR']=data[quant_list].var(axis=1)
	# print_ok("Transformations Complete")

	return data
