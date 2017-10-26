from collections import defaultdict
from math import log, ceil
import random
import numpy as np

scores = []
path_lengths = defaultdict(list)
sample_size = 100
no_trees = 100
height_limit = ceil(log(sample_size, 2))

class Node():
	
	def __init__(self, X, height):
		self.X = X
		self.ranges = get_ranges(X)
		self.height = height
		self.left = None
		self.right = None

	def choose_attribute(self):
		attribute_number = 0
		while True:
			attribute_number += 1
			if attribute_number > len(self.ranges):
				return None, None
			attribute = random.randrange(0, len(self.ranges)) + 1
			range = self.ranges[attribute-1]
			if range[0] != range[1]:
				break
		value = random.randrange(range[0], range[1])
		return attribute, value

	def generate_leaves(self):
		if self.height == height_limit or len(self.X) == 1:
			calculate_path_lengths(self.X, self.height)
			return
		attribute_count = 0
		while True:
			attribute_count += 1
			if attribute_count > len(self.ranges):
				calculate_path_lengths(self.X, self.height)
				return
			attribute, value = self.choose_attribute()
			if attribute == None:
				calculate_path_lengths(self.X, self.height)
				return
			X_left, X_right = self.filter(attribute, value)
			if not check_empty(X_left) and not check_empty(X_right):
				break
		self.left = Node(X_left, self.height+1)
		self.left.generate_leaves()
		self.right = Node(X_right, self.height+1)
		self.right.generate_leaves()

	def filter(self, attribute, value):
		X_left = []; X_right = []
		for x in self.X:
			if ceil(x[attribute]) <= value:
				X_left.append(x)
			else:
				X_right.append(x)
		return np.array(X_left), np.array(X_right)

	def display(self):
		if self.left == None:
			print self.X
		else:
			self.left.display()
			self.right.display()

def check_empty(X):
	if len(X) == 0: return True
	else: return False

def generate_sample(features):
	list = random.sample(range(0,len(features)), min(sample_size,
													 len(features)))
	return features[list, :]

def get_ranges(sample):
	ranges = []
	for i in range(1, len(sample[0])):
		ranges.append([ceil(min(sample[:,i])), ceil(max(sample[:,i]))])
	return ranges

def calculate_path_lengths(X, height):
	global path_lenghts
	path_length = height + average_path_length(X.shape[0])
	for row in X:
		id = row[0]
		path_lengths[id].append(path_length)

def average_path_length(n):
	if n <= 1:
		return 0
	return 2*(log(n-1) + 0.5772156649) - 2*float(n-1)/n

def score_function(expected, average):
	power = -1*float(expected) / average
	return pow(2, power)

def calculate_scores():
	global scores
	average_length = average_path_length(sample_size)
	for key in path_lengths.keys():
		lengths = path_lengths[key]
		expected_length = sum(lengths) / float(len(lengths))
		score = score_function(expected_length, average_length)
		scores.append((key, score))
	scores = sorted(scores, key = lambda x: x[1], reverse = True)

def iForest(features):
	global scores
	global path_lengths
	scores = []
	path_lengths = defaultdict(list)
	forest = []
	for i in range(no_trees):
		sample = generate_sample(features)
		iTree = Node(sample, 0)
		iTree.generate_leaves()
		forest.append(iTree)
	calculate_scores()
	return scores

def forest_outliers(N):
	outliers = scores[:N]
	return [x[0] for x in outliers]

