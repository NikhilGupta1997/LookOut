import pandas as pd
import sys
import random
from helper import *
from system import *

data = pd.read_sas(datafolder + 'fulldata.sas7bdat')

print data

list = random.sample(range(0,41103685), 41103685)
#list = [range(0,41000000)]
newdata = data.ix[list]

print newdata

newdata.to_csv('datrand4.csv', sep='\t')
