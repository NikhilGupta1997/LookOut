import argparse
from data import Feature
from data_transform import read_data
from helper import init_environment
from outliers import calculate_outliers
from plot_functions import generate_scatter_plots
from run_algos import run

""" Parse Arguments to extract data script """
parser = argparse.ArgumentParser(description='Process type of data extraction and datafile')
parser.add_argument("-f", "--datafile", help="the file from which to extract data",
                    action="store", dest="datafile", required=True)
parser.add_argument("-df", "--datafolder", help="the folder containing the datafile",
                    action="store", dest="datafolder", default="Data/")
parser.add_argument("-lf", "--logfolder", help="the folder containing the logfiles",
                    action="store", dest="logfolder", default="Logs/")
parser.add_argument("-pf", "--plotfolder", help="the folder which will contain all the output plots",
                    action="store", dest="plotfolder", default="Plots/")
parser.add_argument("-l", "--logfile", help="the logfile",
                    action="store", dest="logfile", default="log.txt")
parser.add_argument("-d", "--delimiter", help="the csv file delimiter",
                    action="store", dest="data_delimiter", default=",")
parser.add_argument("-b", "--budget", help="Number of plots to display (default 3)",
            		type=int, default='3', dest="budget")
parser.add_argument("-n", "--number", help="Number of outliers to choose (default 10)",
            		type=int, default='10', dest='num_outliers')
parser.add_argument("-p", "--pval", help="Score scaling factor (default 1.0)",
            		action="store", default='1.0', dest='p_val')
parser.add_argument("-s", "--show", help="mention if you want to show all the generated plots",
                    action="store_true", dest="output_plots")
parser.add_argument("-bs", "--baselines", help="mention if you want to run the baselines",
                    action="store_true", dest="baseline")

group_outlier = parser.add_mutually_exclusive_group(required=True)
group_outlier.add_argument("-mrg", "--merge", help="specify columns to include from the data file",
                    action="store_true", dest="merge_ranklists")
group_outlier.add_argument("-if", "--iforests", help="specify columns to include from the data file (default: true)",
                    action="store_true", dest="generate_iForest")
group_outlier.add_argument("-dict", "--dictated", help="specify columns to include from the data file (default: true)",
                    action="store_true", dest="dictated_outliers")

args = parser.parse_args()

""" Initialize Workspace """
init_environment(args)

""" Create features from Data """
features = read_data(args) # from data_transform.py

""" Generate Scatter Plots and Outlier Scores """
rank_matrix, plot_dict = generate_scatter_plots(args, features)

""" Obtain Outliers """
outlier_ids = calculate_outliers(args, features, rank_matrix)

""" Obtain Best Plots """
run(args, features, rank_matrix, plot_dict, outlier_ids)