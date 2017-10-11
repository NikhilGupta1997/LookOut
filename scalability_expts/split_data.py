import os
import numpy as np


for num_edges in np.power(10, range(2,8)):
    print num_edges
    os.system("head -{l} Data/dblp_all.txt > Data/dblp_{n}.txt".format(
    n=num_edges, l=num_edges+1
    ))
