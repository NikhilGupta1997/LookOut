# Scatter Plot Features
identity_features = ["IDs"]
continuous_features = ['SRC', 'DEST', 'EDGES_IN', 'EDGES_OUT', 'LIFE', 'MEDIAN_IAT', 'MEAN_IAT', 'IAT_VAR_MEAN']
discrete_features = []
discription = { 'SRC': 'Unique Sources', \
				'DEST': 'Unique Destinations', \
				'EDGES_IN': '# of Incoming Mails', \
				'EDGES_OUT': '# of Outgoing Mails', \
				'MAX_PROP_IN': 'Single Source Prop.', \
				'MAX_PROP_OUT': 'Single Destination Prop.', \
				'LIFE': 'Lifetime', \
				'MEDIAN_IAT': 'Median IAT', \
				'MEAN_IAT': 'Average IAT', \
				'IAT_VAR_MEAN': 'IAT Variance'}


identity_field = 'SOURCE'
entry_limit = 10 # The minimum entries that must exist per identity item (Set to 0 to disable)
time_series data = True # Calculates lifetimes and IAT data (should be set to false if only one entry per identity)
timestamp_field = 'TIMESTAMP' # Used only if time_series_data is set to true
aggregate_fields = ["WEIGHT"]


