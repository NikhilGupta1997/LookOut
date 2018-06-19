from system import iForest_sample
from sklearn.ensemble import IsolationForest

scores = []
sample_size = iForest_sample

def forest_outliers(N):
	outliers = scores[:N]
	return [x[0] for x in outliers]

def iForest(ids, features):
	global scores
	clf = IsolationForest(max_samples=sample_size)
	clf.fit(features)
	scores = clf.decision_function(features)
	tuples = [ (ids[i], float(0.5 - scores[i])*2.0) for i in range(0, len(ids))]
	scores = sorted(tuples, key = lambda x: x[1], reverse = True)
	return scores