# PlotSpot

## system.py
This is a configuration file which sets the environment and parameters of the code and algorithm. 
+ Files and folders - Define filenames for datafiles. Only *sasfile* should have to be changed by the user 
+ Plot Types - Define the type of plots that you want to have generated on the dataset. Currently the PlotSpot Algorithm only supports Scatter Plots.
+ Scoring Algorithm - How to score outliers in each scatter plot
+ Outlier Defining Algorithm - How to decide on the list of outliers
+ Standadization Algorithm - How to roughly normalize values of outliers obtained from different plots
+ Number of Outliers - A self-defined Threshold on the number of outliers
+ Scatter Plot Features - Define the name and type of features to be extracted form the database

## extract.py
This script is used to read the data in from sas format and converts it into a corresponding csv file. This type conversion needs to be done only one time and the extracted csv file can be used for all further tests on the PlotSpot Code.  

The number of samples to be considered from the large sas datafile can be selected to generate smaller datasets.  

Note) This process will take roughly 30 - 40 minutes to read and write all the data. SAS files take longer to read, hence conversion to csv saves time during code testing.

## data\_transform.py
This will be used to extract features from the dataset and transform the values of certain columns to make the associated data easier to work with.  

Steps: 
+ Read the file into a pandas database.
+ Remove unwanted rows
  + Balance Inquiry Transactions
  + Transactions pertaining to users with less than 5 transactions
+ Create Temporal Features: 
  + TIME\_PERIOD - The Month of the transaction.
  + TRANSACTION\_DATE - The Date of the transaction in datetime format.
  + DAYOFTHEWEEK - ranges from Sunday to Saturday.
  + TRANSACTION\_HOUR - ranges from 0 - 23
+ Fill in missing information in columns:
  + Merchant names left blank are Bank Transactions
+ Calculate the Lifetime of each user
  + Add column for date of first transaction
  + Add column for date of last transaction
  + Add column for lifetime: Duration in days between first and last transactions
+ Get Quantile values for each user
  + 11 rows: 0% to 100% at stepsize of 10%

## graphs
  
