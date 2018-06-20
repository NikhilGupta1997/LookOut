from helper import *

class Feature:
	def __init__( self, name, data, ids ):
		self.name = name
		self.description = name
		self.type = 0 # Type can be either {continuous:0, discrete:1, time_series:2}
		self.log = False # Whether the data is to be represented in log scale
		self.analytics = {}
		self.set_data( data )
		self.ids = ids

	def get_name( self ):
		return self.name

	def get_description( self ):
		return self.description

	def set_description( self, desc ):
		self.description = desc

	def get_type( self ):
		return self.type

	def set_type( self, typ ):
		self.type = typ

	def get_log( self ):
		return self.log

	def set_log( self, val ):
		self.log = val

	def get_data( self ):
		return self.data

	def set_data( self, data, type=None, log_val=None ):
		self.data = data
		self.analyse_data( type )
		if log_val:
			self.set_log( log_val )
		else:
			self.predict_scale()

	def get_ids( self ):
		return self.ids

	def get_analytics( self ):
		return self.analytics

	def analyse_data( self, type=None ):
		self.analytics['min'] = get_min( self.data )
		self.analytics['max'] = get_max( self.data )
		self.analytics['median'] = get_median( self.data )
		self.analytics['mean'] = get_mean( self.data )
		self.analytics['std_dev'] = get_std_dev( self.data )

	def predict_scale( self ):
		upper_diff = self.analytics['max'] - self.analytics['median']
		lower_diff = self.analytics['median'] - self.analytics['min']
		ratio = float( upper_diff / lower_diff )
		if  ratio > 10.0 or ratio < 0.1:
			self.set_log( True )