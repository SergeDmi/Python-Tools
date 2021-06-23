#!/usr/bin/env python3
####### PACKAGES
import pandas as pd
import sys

if __name__=="__main__":
	"""
	$ python3 gather_csvs.py FILE.CSV [FILE2.CSV  ... FILEN.CSV] [out=NAME.CSV]
		Concatenates several csv files into one.
	"""

	args = sys.argv[1:]
	options = []
	files = []

	for arg in args:
		if arg.find('=') > 0 or arg.startswith('-'):
			options.append(arg)
		else:
			files.append(arg)

	# Default filenames and options
	export_file = 'gathered.csv'

	for opt in options:
		if opt.startswith('out='):
			export_file = opt[4:]

	fname=files[0]
	nf = len(files)

	ex_data = pd.read_csv(fname,squeeze=True, index_col=0)
	keys = ex_data.columns.to_list()
	datas = pd.DataFrame(columns=keys)

	for i, fname in enumerate(files):
		ex_data = pd.read_csv(fname, squeeze=True, index_col=0)
		datas = datas.append(ex_data,)

	# Exporting gathered  file
	datas.to_csv(export_file)
