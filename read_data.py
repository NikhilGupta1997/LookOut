from __future__ import print_function

import pandas as pd
import sys
from data import Feature
from feature_file import *
from helper import *


def read_data(args):
	print( "\nFilename = ", end='' ); cprint(args.datafile, OKGREEN)
	
	# Read data from csv file
	cprint("Reading File")
	data = pd.read_csv(args.datafolder + args.datafile, delimiter=args.data_delimiter) # Be patient, takes some time
	print_ok( "CSV File Read Complete" )

	""" TRANSFORMATIONS """
	cprint("Transformations")

	# Group by identity field
	print( "\t-> Group by identity field: " + identity_field )

	if entry_limit:
		# Remove unwanted rows
		print( "\t-> Removing Unwanted Rows" )
		data = data[data.groupby(identity_field)[identity_field].transform(len)>=entry_limit]

	if time_series_data:
		# Calculate Time Series Metrics
		data.insert(0,'FIRST_TRANSMISSION_DATE', data.groupby(identity_field)[timestamp_field].transform(lambda x: min(x)))
		data.insert(1,'LAST_TRANSMISSION_DATE', data.groupby(identity_field)[timestamp_field].transform(lambda x: max(x)))
		data['LIFETIME'] = (data['LAST_TRANSMISSION_DATE'] - data['FIRST_TRANSMISSION_DATE']) # Add column for user lifetime
		data = data[data.LIFETIME > 0]

		# Add IAT information
		print( "\t-> Adding IAT Information" )
		data = data.sort_values([identity_field,timestamp_field])
		data['NEXT_TIMESTAMP'] = data.groupby(identity_field)[timestamp_field].shift(-1)
		data['IAT'] = data['NEXT_TIMESTAMP'] - data['TIMESTAMP']
		data.insert(0,'MEAN_IAT', data.groupby(identity_field)['IAT'].transform(lambda x: mean(x)))
		data.IAT.fillna(data.MEAN_IAT, inplace=True)

		# Add Quantile information based on Amount Spent by the User
		print( "\t-> Adding IAT Quantile Information" )
		update_progress(0, 11)
		quant_list = []
		for i in range(11):
			data.insert(i,'QUANTILE_' + str(10*i), data.groupby(identity_field).IAT.transform(lambda x: quantile(x)[i]))
			quant_list.append('QUANTILE_' + str(10*i))
			update_progress(i+1, 11)
		data['IAT_VAR_MEAN']=data[quant_list].var(axis=1)
		data['MEDIAN_IAT']=data[quant_list[5]]
		print_ok("Transformations Complete")

	""" Create Feature Objects """
	cprint("Creating Features")
	features = {}

	# Get ids mapping to identities
	print( "\t-> Getting Object Ids" )
	print( "\t\t-> ", end='' );
	objects = data.groupby(identity_field)
	ids = objects.groups.keys()
	stats = objects.size().reset_index(name='counts')
	COUNT = stats['counts'].values.tolist()
	if data_not_flat(COUNT):
		features['COUNT'] = Feature('COUNT', COUNT, ids)
		cprint("COUNT", OKBLUE)
	else:
		cprint('COUNT', FAIL)

	if time_series_data: # Add all time series metric features
		print( "\t-> Creating Temporal Features" )
		print( "\t\t-> ", end='' )
		LIFETIME = objects['LIFETIME'].first().values.tolist()
		if data_not_flat(LIFETIME):
			features['LIFETIME'] = Feature('LIFETIME', LIFETIME, ids)
			cprint('LIFETIME', OKBLUE, end='  ')
		else:
			cprint('LIFETIME', FAIL, end='  ')
		IAT_VAR_MEAN = objects['IAT_VAR_MEAN'].first().values.tolist()
		if data_not_flat(IAT_VAR_MEAN):
			features['IAT_VAR_MEAN'] = Feature('IAT_VAR_MEAN', IAT_VAR_MEAN, ids)
			cprint('IAT_VAR_MEAN', OKBLUE, end='  ')
		else:
			cprint('IAT_VAR_MEAN', FAIL, end='  ')
		MEAN_IAT = objects['MEAN_IAT'].first().values.tolist()
		if data_not_flat(MEAN_IAT):
			features['MEAN_IAT'] = Feature('MEAN_IAT', MEAN_IAT, ids)
			cprint('MEAN_IAT', OKBLUE, end='  ')
		else:
			cprint('MEAN_IAT', FAIL, end='  ')
		MEDIAN_IAT = objects['MEDIAN_IAT'].first().values.tolist()
		if data_not_flat(MEDIAN_IAT):
			features['MEDIAN_IAT'] = Feature('MEDIAN_IAT', MEDIAN_IAT, ids)
			cprint('MEDIAN_IAT', OKBLUE, end='  ')
		else:
			cprint('MEDIAN_IAT', FAIL, end='  ')

	# Create Feature Object for individual data fields
	print( "\n\t-> Creating Aggregate Features" )
	for field in aggregate_fields:
		print( "\t\t-> ", end='' )
		values = objects[field].sum().values.tolist()
		if data_not_flat(values):
			features[field] = Feature(field, values, ids)
			cprint(field, OKBLUE, end='  ')
			if time_series_data: # Calculate extra metrics
				values = objects[field].mean().values.tolist()
				name = field + '_MEAN'
				if data_not_flat(values):
					features[name] = Feature(name, values, ids)
					cprint(name, OKBLUE, end='  ')
				else:
					cprint(name, FAIL, end='  ')
				values = objects[field].var().values.tolist()
				name = field + '_VAR'
				if data_not_flat(values):
					features[name] = Feature(name, values, ids)
					cprint(name, OKBLUE, end='  ')
				else:
					cprint(name, FAIL, end='  ')
		else:
			cprint(field, FAIL, end='  ')

	# Create Feature Object for individual object fields
	print( "\n\t-> Creating Object Features" )
	print( "\t\t-> ", end='' )
	for field in object_fields:
		values = objects[field].nunique().values.tolist()
		if data_not_flat(values):
			features[field] = Feature(field, values, ids)
			cprint(field, OKBLUE, end='  ')
		else:
			cprint(field, FAIL, end='  ')
	print()
	
	if len(features) != 0:
		print_ok("Feature Creation Complete")
		return features
	else:
		print_fail("No Features were Created. Exiting...")
		sys.exit()