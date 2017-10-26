""" Define System Variables """

# Files and Folders
sasfile = 'fulldata.sas7bdat' 	# SAS Data File name	
datafile = 'enron.csv'		# Data File name
datafolder = 'Data/' 			# Data Folder
filefolder = 'Files/'			# Files Folder
plotfolder = 'Plots/'			# Plot Folder
outputfile = 'outlier-plot.txt'	# Outputfile Name for outlier-plot graph
coverfile = 'outlier-cover.txt'	# Outputfile Name for outlier-plot graph
rankfile = '_ranks.txt'			# Outpufile for individual plot outlier scores
frequencyfile = 'freq.txt'		# Frequency file for outliers in focus
logfile = 'log.txt'				# Log File Name

data_delimiter = ','			# Define delimiter for csv datafile

# Which Plot Types to Generate
scatter_show = True 			# Generate Scatter Plots
ccdf_show = False				# Generate CCDF Plots
hist_show = False				# Generate Histograms
time_series_show = False		# Generate Time Series Plots
band_show = False				# Generate Band Plots

# Which Scoring Algortihm to use
algo_oddball = False			# Oddball outlier scoring algo
algo_iForests = True			# Depth based scoring algo

# Which Outlier Choosing Algorithm to use
merge_ranklists = False					# Merge ranks of each outlier
generate_iForest = True					# Use iForests on all features
global_outlier_list = [127, 128, 129] 	# Used if both algorithms set to false

# Which Standardization Algorithm to use
max_divide = False 				# Divide weights by max ranked weight
quantile_divide = True			# Divide into quantiles and quantiles have differnet weights
quantile_bins = 20 				# Number of Quantiles to divide scores

# System Variables
N_list = [20] 		# List of Number of Outliers
Budget = [2, 3]			# List to define budgets
iForest_sample = 256			# iForest Tree Sample Size
P_val = 1						# Scaling factor
output_plots = True				# Choose to show plots

# Baselines
baseline =	True 				# Use baseline selection or not

# Scatter Plot Features
identity_features = ["IDs"]
continuous_features = ['AMOUNT', 'DEST', 'LIFE', 'IN_EDGE', 'IAT_VAR']
discrete_features = []
compare_value = {'AMOUNT':1, 'DEST':1, 'LIFE':1, 'IN_EDGE':1, 'IAT_VAR':1}
discription = { 'AMOUNT': 'Total Amount of Transmission', \
				'DEST': 'No. of Unique Destinations', \
				'LIFE': 'Lifetime', \
				'IAT_VAR': 'InterArrival Time Variation', \
				'IN_EDGE': 'No. of interactions'}

# Plot Marker Specifications
colors = {0: '#33b8ff', 1: '#e67e22', 2: '#a569bd', 3: '#8aff33', 4: '#f6ff33'}
outlier_color = {0: '#cce6ff', 1: '#FF4500'}
shapes = {0: '^', 1: '.', 2: 's', 3: '*'}
sizes = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9}
blue_circle = 30

# Terminal Colors
RED = "\033[31m"
BLUE = "\033[34m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
VIOLET = "\033[35m"
RESET = "\033[0;0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
REVERSE = "\033[7m"
HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKGREEN = "\033[92m"
CYAN = "\033[96m"
WARNING = "\033[93m"
FAIL = "\033[91m"

