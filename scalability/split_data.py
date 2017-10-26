import os
import numpy as np


for num_edges in np.power(10, np.linspace(2, 8, 13)).astype(int):
    print num_edges
    os.system("head -{l} Data/dblp_all.txt > Data/dblp_{n}.txt".format(
    n=int(num_edges), l=int(num_edges)+1
    ))
