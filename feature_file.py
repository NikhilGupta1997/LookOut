identity_field = 'SOURCE'
entry_limit = 10 # The minimum entries that must exist per identity item (Set to 0 to disable)
time_series_data = True # Calculates lifetimes and IAT data (should be set to false if only one entry per identity)
timestamp_field = 'TIMESTAMP' # Used only if time_series_data is set to true
aggregate_fields = ["WEIGHT"]
object_fields = ["DESTINATION"]

outlier_list = [126, 128]