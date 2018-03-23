from pyaofit import *

def printVerbose(string):
	if printVerbose._verbose:
		print(string)
printVerbose._verbose = False

def makePrintVerbose(verbose):
	printVerbose._verbose = verbose
