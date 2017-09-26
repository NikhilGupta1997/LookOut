import pandas as pd
import sys
from helper import *
from system import *

def read_data():
	print "Filename = ",
	cprint(datafile, OKGREEN)
	
	#Read data from csv file
	cprint("Reading File")
	enable_warnings()
	data = pd.read_csv(datafolder + datafile, delimiter='\t', index_col=0)
	#data = pd.read_sas(datafolder + datafile)
	disable_warnings()
	print_ok("File Read Complete")

	""" TRANSFORMATIONS """
	cprint("Transformations")
	#Remove unwanted rows
	print "	-> Removing Unwanted Rows"
	data = data[data.TRANSACTION_AMOUNT != 0] #Remove The Balance Inquiry Entries
	data = data[data.groupby('ACCT_KEY').ACCT_KEY.transform(len)>1] #Remove the entries with less than 10 transactions

	#Transform Dates to usable forms
	print "	-> Transforming Date Values"
	data['Z_LOAD_DATE'] = pd.to_timedelta(data['Z_LOAD_DATE'], unit='s') + pd.datetime(1960,1,1) #Convert SAS date to datetime
	data['TIME_PERIOD'] = pd.to_timedelta(data['TIME_PERIOD'], unit='D') + pd.datetime(1960,1,1) #Convert SAS date to datetime
	data['TIME_PERIOD'] = data.TIME_PERIOD.map(lambda x: x.strftime('%Y-%m'))
	data['TRANSACTION_DATE'] = pd.to_timedelta(data['TRANSACTION_DATE'], unit='D') + pd.datetime(1960,1,1) #Convert SAS date to datetim
	data['DAYOFWEEK'] = data['TRANSACTION_DATE'].apply(lambda x: x.dayofweek) #Add column for day of the week of transaction
	data['TRANSACTION_HOUR'] = pd.to_datetime(data['TRANSACTION_POST_TIME'].astype(str).apply(lambda x: x.zfill(6)), format = '%H%M%S').dt.hour

	#Fill Missing Data
	print "	-> Filling Missing Information"
	data['MERCHANT_NAME_SCRUB'] = data['MERCHANT_NAME_SCRUB'].fillna('BANK TRANSACTION') #Fill names for all stores

	#Add User Lifetime Detail Columns
	print "	-> Calculating Lifetimes"
	data.insert(0,'FIRST_TRANSACTION_DATE', data.groupby('ACCT_KEY')['TRANSACTION_DATE'].transform(lambda x: min(x)))
	data.insert(1,'LAST_TRANSACTION_DATE', data.groupby('ACCT_KEY')['TRANSACTION_DATE'].transform(lambda x: max(x))) 
	data['LIFETIME'] = (data['LAST_TRANSACTION_DATE'] - data['FIRST_TRANSACTION_DATE']).abs().dt.days #Add column for user lifetime
	
	#Add Quantile information based on Amount Spent by the User
	print "	-> Adding Quantile Information"
	users = data.groupby('ACCT_KEY')
	update_progress(0, 11)
	for i in range(11):
		data.insert(i,'QUANTILE_' + str(10*i), users.TRANSACTION_AMOUNT.transform(lambda x: quantile(x)[i]))
		update_progress(i+1, 11)
	print_ok("Transformations Complete")

	return data
