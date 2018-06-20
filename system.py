# Scatter Plot Features
identity_features = ["IDs"]
continuous_features = ['SRC', 'DEST', 'EDGES_IN', 'EDGES_OUT', 'LIFE', 'MEDIAN_IAT', 'MEAN_IAT', 'IAT_VAR_MEAN']
discrete_features = []
compare_value = {'SRC':1, 'DEST':1, 'EDGES_IN':1, 'EDGES_OUT':1, 'MAX_PROP_IN':1, 'MAX_PROP_OUT':1, 'LIFE':1, 'MEDIAN_IAT':1, 'MEAN_IAT':1, 'IAT_VAR_MEAN':1}
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