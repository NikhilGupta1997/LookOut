from __future__ import print_function

import sys

# Plot Marker Specifications
outlier_color = {0: '#cce6ff', 1: '#FF4500'}
outlier_circle_size = 40

# Terminal Colors
RED = "\033[31m"
BLUE = "\033[34m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
VIOLET = "\033[35m"
RESET = "\033[0;0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
REVERSE = "\033[7m"
HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKGREEN = "\033[92m"
CYAN = "\033[96m"
WARNING = "\033[93m"
FAIL = "\033[91m"

def enable_warnings():
	sys.stdout.write(WARNING)
	print( "..." )

def disable_warnings():
	sys.stdout.write(RESET)

def start_color(color):
	sys.stdout.write(color)

def end_color():
	sys.stdout.write(RESET)

def print_ok(text):
	end_color()
	print( "[ ", end='' )
	start_color(OKGREEN)
	print( "OK", end='' )
	end_color()
	print( " ] ", end='' )
	print( text )

def print_fail(text):
	end_color()
	print( "[ ", end='' )
	start_color(FAIL)
	print( "FAIL", end='' )
	end_color()
	print( " ] ", end='' )
	print( text )

def cprint(text, color=CYAN, end=None):
	if color == CYAN:
		print()
	start_color(color)
	print(text, end=end)
	end_color()

def update_progress(current, max):
	start_color(BOLD)
	progress = float(current) / max
	barLength = 10
	block = int(round(barLength*progress))
	text = "\rPercent: [{0}] {1:.2f}%".format( "#"*block + "-"*(barLength - block) , progress*100)
	sys.stdout.write(text)
	sys.stdout.flush()
	if progress == 1:
		sys.stdout.write("\r")
	end_color()