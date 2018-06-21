from __future__ import print_function

import pandas as pd
import sys
from data import Feature
from helper import *
from system import *

def read_data(args):
	print( "Filename", end='' ); cprint(args.datafile, OKGREEN)
	data = pd.read_csv(args.datafolder + args.datafile, delimiter=args.data_delimiter) # Be patient, takes some time
	print_ok( "CSV File Read Complete" )

	""" TRANSFORMATIONS """
	cprint("Transformations")

	# Group by identity field
	print( "\t-> Group by identity field: " + identity_field )
	data = data.groupby(identity_field)

	if entry_limit:
		# Remove unwanted rows
		print( "\t-> Removing Unwanted Rows" )
		data = data[data[identity_field].transform(len)>=entry_limit]

	# Get ids mapping to identities
	print( "\t-> Getting object ids" )
	ids = data.groups.keys()

	print(ids)



