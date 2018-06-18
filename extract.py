import argparse
import csv
import os.path
import pandas as pd
import sys
import random
from helper import *
from system import *

# Parse Arguments to extract data script
parser = argparse.ArgumentParser(description='Process type of data extraction and datafile')
parser.add_argument("-f", "--datafile", help="the file from which to extract data",
                    action="store", dest="file", default="")
parser.add_argument("-t", "--targetfile", help="the file to export the data",
                    action="store", dest="target_file", default="target.csv")
parser.add_argument("-m", "--mode", help="specify type of extraction {full, partial, random}; (default: full)",
                    action="store", dest="mode", default='full')
parser.add_argument("-p", "--portion", help="fraction of data to extract. Only valid in partal or random modes (default 1.0)",
                    action="store", default='1.0')
group = parser.add_mutually_exclusive_group()
group.add_argument("-i", "--include", help="specify columns to include from the data file (default: include all)",
                    action="append", dest="include")
group.add_argument("-e", "--exclude", help="specify columns to exclude from the data file (default: exclude none)",
                    action="append", dest="exclude")
args = parser.parse_args()

### Validate Input Arguments From User ###
# Check if the datafile exists
datafile = datafolder + args.file
if os.path.isfile(datafile):
	print_ok("Datafile \"" + datafile + "\" successfully found")
else:
	print_fail("Datafile \"" + datafile + "\" was not found")
	sys.exit(1)

# Check if mode is valid
if args.mode not in ['full', 'partial', 'random']:
	print_fail("The mode \"" + args.mode + "\" is not valid")
	parser.print_help()
	sys.exit(1)
print_ok("Data procesing in " + args.mode + " mode")

# Validate the portion of data to be extracted
try:
	portion = float(args.portion)
	try:
		assert (portion <= 1.0 and portion > 0.0)
	except AssertionError as e:
		print_fail("AssertionError")
		raise
	print_ok("Portion of file to be read = " + str(portion))
except ValueError:
	print_fail("\"" + args.portion + '\" not a valid float value. Moving forward with default value of 1.0')
	portion = 1.0

# Get Fields of the file as specified by the User
if args.include or args.exclude:
	with open(datafile, 'rU') as f:
		headers = csv.DictReader(f).fieldnames
	if args.include:
		for field in args.include:
			if field in headers:
				continue
			else:
				print_fail("The field \"" + field + "\" not found in csv header")
				sys.exit(1)
		headers = args.include
	if args.exclude:
		for field in args.exclude:
			if field in headers:
				headers.remove(field)
				continue
			else:
				print_fail("The field \"" + field + "\" not found in csv header")
				sys.exit(1)

	print_ok("The field names to be read are : " + str(headers))

### Retreive Data ###
# Read data from csv file and store into a pandas dataframe
try:
	df = pd.read_csv(datafolder + args.file)
	print_ok("\"" + args.file + "\" successfully read")
except Exception as e:
	print_fail("Parse Error")
	raise

# Select specific columns from dataframe
if headers:
	df = df[headers]
	print_ok("Specified columns selected")

# Select specific rows from dataframe
row_size = df.shape[0]
new_row_size = int(row_size*portion)
if args.mode == 'partial':
	df = df.head(new_row_size)
	print_ok("Total of " + str(new_row_size) + " rows selected from head of dataframe")
elif args.mode == 'random':
	indecies = random.sample(range(0,row_size), new_row_size)
	df = df.ix[indecies]
	print_ok("Total of " + str(new_row_size) + " rows selected randomly form dataframe")

print_ok("Data transformed to specifications. Final shape: " + str(df.shape))

### Export Data ###
df.to_csv(datafolder + args.target_file, sep='\t')
print_ok("Data written to file \"" + args.target_file + "\"")
