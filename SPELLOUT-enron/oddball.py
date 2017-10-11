import numpy as np
from math import log, isnan

def line_value(x1, x2, y1, y2, x):
	if x1 == x2:
		return float(y1 + y2) / 2
	return (float(y2 - y1)/(x2 - x1))*x + float(y1*x2 - y2*x1)/(x2 - x1)

def get_scores(median_X, median_Y, X, Y, IDs):
	scores = []
	for i, bin in enumerate(np.digitize(X, median_X)):
		x = X[i]; y = Y[i]; id = IDs[i]
		if bin == 0:
			C = line_value(median_X[0], median_X[1], median_Y[0], median_Y[1], x)
		elif bin == len(median_X):
			C = line_value(median_X[bin-2], median_X[bin-1], median_Y[bin-2], median_Y[bin-1], x)
		else:
			C = line_value(median_X[bin-1], median_X[bin], median_Y[bin-1], median_Y[bin], x)
		score = (float(max(y, C)) / (min(y, C))) * log(abs(y - C) + 1)
		scores.append((id, float("{0:.2f}".format(score))))
	return sorted(scores, key=lambda x: x[1], reverse=True)
