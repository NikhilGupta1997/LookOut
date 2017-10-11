import pandas as pd
import sys
import random
from helper import *
from system import *

# Read from SAS style datafile
data = pd.read_sas(datafolder + sasfile)
print data

# Select Sample size 
num_samples = 41103685
list = random.sample(range(0,41103685), num_samples)

# Select sample data
newdata = data.ix[list]
print newdata

# Add data to CSV file (easy to work with w.r.t. SAS data files)
newdata.to_csv(datafolder + datafile, sep='\t')
