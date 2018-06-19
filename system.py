""" Define System Variables """

# Files and Folders
datafile = 'enron.csv'			# Data File name
datafolder = 'Data/' 			# Data Folder
logfolder = 'Logs/'				# Logs Folder
plotfolder = 'Plots/'			# Plot Folder
logfile = 'log.txt'				# Log File Name

data_delimiter = ','			# Define delimiter for csv datafile

# Which Scoring Algortihm to use
algo_oddball = False			# Oddball outlier scoring algo
algo_iForests = True			# Depth based scoring algo

# Which Outlier Choosing Algorithm to use
merge_ranklists = False					# Merge ranks of each outlier
generate_iForest = True					# Use iForests on all features
global_outlier_list = [53, 107, 122, 127, 150] 		# Used if both algorithms set to false

# Which Standardization Algorithm to use
max_divide = False 				# Divide weights by max ranked weight
quantile_divide = True			# Divide into quantiles and quantiles have differnet weights
quantile_bins = 20 				# Number of Quantiles to divide scores

# System Variables
N_list = [10, 20, 30, 40] 		# List of Number of Outliers
Budget = [1,2,3,4,5,6]			# List to define budgets
iForest_sample = 64				# iForest Tree Sample Size
P_val = 1						# Scaling factor
output_plots = True 			# Choose to show plots

# Baselines
baseline =	True 				# Use baseline selection or not

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