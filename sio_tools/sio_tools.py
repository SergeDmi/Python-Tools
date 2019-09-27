# -*- coding: utf-8 -*-
#!/usr/bin/env python
import math
from numpy import *
import subprocess
import os.path
import sys
import os
import warnings
import copy


__VERSION__ = "0.1.5"

try:
	import pandas as pd
except:
	print('Warning : Could not import pandas module')
	print('Importing csv and xls will not work')

# @TODO : use *args,**kwargs EVERYWHERE
# @TODO : replace all the concatenate with os.join()
# @TODO : better cleanup and stuff

__exclude_key__=["__EXCLUDE_KEY__"]
__COMMENTS__=["#","%"]

"""
# SYNOPSIS

   Simple custom i/o utilities

# DESCRIPTION

   There are much better ways to do, but these do i/o as I wish
"""


## Warning tools
def current_version():
    return __VERSION__

def custom_warn(message):
	warnings.formatwarning = simp_formatwarning
	warnings.warn(message)

def simp_formatwarning(message, *args, **kwargs):
    # A very simple sarning with just a message
	# without showing the warning line
    return ('WARNING : ' + str(message) + '\n')

def empty_out_data():
	return {'data' : [],'labels' : [],'size_x' : 0, 'size_y' : 0, 'body' : [], 'header' : []}

## Always good to have a modulo function
def modulo(k,n):
	c=0
	while k>=n:
		k=k-n
		c=c+1
	return k,c

## General tools for running jobs

# make a file executable ; Python only
def make_exec(fname):
	return run("chmod +x "+fname)

#Runs a unic command and returns the stdout
def unpy(job):
	if not type(job)==list:
		job=[job]
	proc=subprocess.Popen(job,stdout=subprocess.PIPE)
	return proc.stdout.readlines()


#pwd
def pwd():
	lines=unpy('pwd')
	return clean_line(lines[0])

# folder
def last_pwd():
	fold=pwd()
	fold=fold.rstrip('/')
	words=fold.split('/')
	return words[-1]

#create job list from index a to index b
#fname/index/ename is absolute adress of the executable
def bjarray(jname,fname,ename,a,b):
	fname=conc(fname,'\$LSB_JOBINDEX',ename)
	return r'bsub -J "%s[%s-%s]" %s -o /g/nedelec/dmitrief/clustero/output' %(jname,a,b,fname)

# create job lists, to improve
def bjobs(jname,fname,ename,jvals):
	return bjarray(jname,fname,ename,min(jvals),max(jvals))


#Removes extension from file
def remove_ext(fname):
	words=fname.split(".")
	l=len(words)
	if len(words)<3:
		return words[0]
	else:
		return "".join(word+"." for word in words[0:l-1])

# Archive a folder with tar
def archive(fname):
	job="tar -czf %s.tgz %s && rm -R %s" %(remove_ext(clean_name(fname)),fname,fname)
	run(job)
	return


#runs a bash line
def run(job):
	subprocess.call([job],shell=True)

#create a folder with a name name
def mkdir(name):
	if ~(os.path.isdir(name)):
		job="%s%s" % ("mkdir ",name)
		run(job)
	return

#copies files to the folder fn
def copy_files(fn,files):
	for f in files:
		fname=conc(fn,f)
		job="cp %s %s" % (f,fname)
		run(job)
	return

#writes lines in a file in a folder
def write_file(file_name,lines):
	fname=conc(folder_name,file_name)
	f=open(fname,'w')
	for line in clean_lines(lines):
		f.write(line+"\n")
	f.close()
	return

## Word processing
# Replace some words by others in a set of strings (lines)
def switch_words_in_lines(lines,dict):
	return [switch_words(line,dict) for line in lines]

# Replace some words by others in a single string (line)
def switch_words(line,dict):
	for key,value in dict.items():
		if line.find(key)>=0:
			words=line.split(key)
			return ''.join([words[0],value,words[1]])
	return line

# Cleanup a word ...
# @TODO ; to be improved !!!!
def word_cleanup(word):
	word =word.replace(",","")
	word =word.replace(" ","")
	word =word.replace(")","")
	return word

# Remove / at the end of folder names
def clean_name(fname):
	l=len(fname)
	if l and fname.find("/")==l-1:
		return fname[0:l-1]
	else:
		return fname

# Remove commented lines / line sections
def remove_comments(lines,comments=__COMMENTS__,**kwargs):
	comments=__COMMENTS__
	for c in comments:
		l=len(lines)
		j=0
		while l>0 and j<l:
			k=lines[j].find(c)
			if k>0:
				#print "Corrected midle"
				lines[j]=lines[j][:k]
				if len(lines[j].split()):
					j=j+1
				else:
					lines.pop(j)
					l=l-1
			elif k==0:
				lines.pop(j)
				l=l-1
			else:
				j=j+1
				#print "uncorrected"
	return lines


# Remove commented lines / line sections
def lines_remove_comments(lines,comments=__COMMENTS__,**kwargs):
	new_lines=[]
	for line in lines:
		new_line=line_remove_comments(line,comments=comments,**kwargs)
		if new_line:
			new_lines.append(new_line)
	return new_lines

def line_remove_comments(line,comments=__COMMENTS__,**kwargs):
	for c in comments:
		k=line.find(c)
		if k>0:
			line=line[:k]
		elif k==0:
			line=''
	return line

# generates arguments and keyword arguments from arguments (e.g. sys.argv[1:])
def make_args_and_kwargs(arguments):
	args=[]
	if len(arguments)>0:
		kwingredients=[]
		for arg in arguments[1:]:
			jcvd=arg.split('=')
			n=len(jcvd)
			if n==1:
				args.append(arg)
			else:
				if n>2:
					jcvd=[jcvd[0],''.join(jcvd[1:])]
				kwingredients.append(jcvd)
		kwargs=dict(kwingredients)
	else:
		kwargs={}
	return args,kwargs

# Concatenate folder names, being carefull of the "/" at the end
#@TODO : use os.join !!!!!!
def conc(*names):
	l=len(names)
	if l>1:
		return "%s/%s" % (clean_name(names[0]),conc(*names[1:l]))
	else:
		return names[0]

# Remove end-of-line (\n) for a string
def clean_word_list(words):
	tags=['','\n']
	return [word for word in words if word not in tags]


def clean_line(line):
	#while line.find("\n")>-1:
	line=line.rstrip("\n")
	return line

# Remove end-of-lines (\n) for an array of strings
def clean_lines(lines):
	for i,line in enumerate(lines):
		lines[i]=clean_line(line)
	return [line for line in lines if line and not line.isspace()]


#creates an array of numbers equi valent to matlab minA:stepA:maxA
def create_array(minA,maxA,stepA):
	ar=arange(minA,maxA,stepA)
	l=len(ar)
	if ar[l-1]!=maxA:
		ar=append(ar,maxA)
		l=l+1
	return ar,l

# Check if string a can be converted to float
def isnum(a):
	try:
		float(a)
	except ValueError:
		return False
	return True

# Converts line of space separated value to vector
def nums(line):
	words=line.split()
	re=[]
	if len(words):
		for w in words:
			if isnum(w):
				re.append(float(w))
	return re
	#return map(float,line.split())

# Check if word exists in file
def isword_file(fname,word):
	lines=getlines(fname)
	return isword_lines(lines,word)

# makes a file list in current folder
#@TODO : deprecate this shit
def make_file_list(part_fname,outro):
	liste=[]
	l=len(part_fname)
	for f in os.listdir('.'):
		ix=f.find(part_fname)
		if ix>=0:
			bli=f.find(outro)
			if bli>=0:
				numero=f[ix+l:bli]
			else:
				numero=f[ix+l]
			try:
				liste.append([int(numero),f])
			except:
				print('Could not understand the number %s in file %s' %(numero,f))
	#we order the list by time stamp
	return liste

# Now we're talking
# makes a file list recursively with include and exclude options !
#@TODO : document
#@TODO : search depth
def make_recursive_file_list(folder='.',include=[''],ext='',exclude=__exclude_key__,**kwargs):
	liste=[]
	dict=kwargs
	if not type(include)==list:
		include=[include]
	if not type(exclude)==list:
		exclude=[exclude]

	for f in os.listdir(folder):
		f=os.path.join(folder,f)
		if os.path.isdir(f):
			dict['folder']=f
			dict['ext']=ext
			dict['include']=include
			dict['exclude']=exclude
			liste+=make_recursive_file_list(**dict)
		#elif f.find(include)>=0 and f.endswith(ext) and f.find(exclude)<0:
		elif f.endswith(ext):
			is_included=[f.find(inc)>=0 for inc in include]
			is_not_excluded=[f.find(exc)<0 for exc in exclude]
			if all(is_included) and all(is_not_excluded):
				liste+=[f]
	return liste

# Just order stuff
def make_ordered_file_list(part_fname,outro):
	liste=make_file_list(part_fname,outro)
	liste.sort(key=lambda tup: tup[0])
	return liste

# Important for analysis
# makes a list of properties  from a config file of name file_name
# properties are identified by keyword key
def make_prop_dict(fname,key):
	lines=getlines(fname)
	props={}
	for line in lines:
		words=line.split()
		ixes=[i for i,word in enumerate(words) if word.find(key)>=0]
		for i in ixes:
			try:
				props[words[i+1]]=line_remove_comments(clean_line(''.join(words[i+2:])))
			except:
				print('Could not understand property %s from configuration file %s' %(words[i],fname))
	#for line in lines1:
	return props

# Check if word exist in lines
def isword_lines(lines,word):
	for li in lines:
		if li.find(word)>-1:
			return 1
	return 0

#def get lines from file
def getlines(fname):
	f=open(fname,'r')
	lines=f.readlines()
	f.close()
	return lines

# decomposes a file into body and header
def decompose_file(fname,comments=__COMMENTS__,**kwargs):
	lines=clean_lines(getlines(fname))
	head_lines=[]
	body_lines=[]

	for line in lines:
		is_header=0
		for c in comments:
			if line.find(c)>=0:
				head_lines.append(line)
				is_header=1
		if not is_header:
			body_lines.append(line)

	return body_lines,head_lines

def get_data_and_header(fname):
	(body,header)=decompose_file(fname)
	head=header[-1]
	data=getdata_lines(body)
	return data,head

def make_nice_headers(heads,comments=__COMMENTS__,**kwargs):
	return [clean_head(head,comments=comments,**kwargs) for head in heads if head not in comments]

def clean_head(head,comments=__COMMENTS__,**kwargs):
	if head:
		for c in comments:
			f=head.find(c)
			if f>-1:
				head=head[f+len(c):]
	return head

def splitheader(fname):
	heads=getheader(fname)
	if heads:
		heads=heads.split(' ')
		return make_nice_headers(heads)
	else:
		return []

def split_header(heads):
	if heads:
		heads=heads[-1]
		heads=heads.split(' ')
		return make_nice_headers(heads)
	else:
		return []

def data_import_wrapper(fname,**kwargs):
	if fname.endswith('.txt'):
		return txt_import_wrapper(fname,**kwargs)
	elif fname.endswith('.csv'):
		return csv_import_wrapper(fname,**kwargs)
	elif fname.endswith('.xls') or fname.endswith('.xlsx'):
		return xls_import_wrapper(fname,**kwargs)
	else:
		try:
			return txt_import_wrapper(fname,**kwargs)
		except:
			raise ValueError('Unsupported format for file %s'  %fname)
			return empty_out_data()

def txt_import_wrapper(fname,**kwargs):
	(body_lines,head_lines)=decompose_file(fname,**kwargs)
	(data,sx,sy)=getdata_lines(body_lines,**kwargs)
	return {'data' : data , 'labels' : split_header(head_lines), 'size_x' : sx , 'size_y' : sy , 'body' : body_lines , 'header' : head_lines}

def csv_import_wrapper(fname,**kwargs):
	frames=pd.read_csv(fname)
	return import_from_frames(frames)

def xls_import_wrapper(fname,**kwargs):
	custom_warn('Excel support very limited')
	frames=pd.read_excel(fname)
	return import_from_frames(frames)

def import_from_frames(frames):
	cols=frames.columns.values
	labels=[word for word in cols]
	data=frames.values
	sx,sy=data.shape
	return {'data' : data , 'labels' : labels, 'size_x' : sx , 'size_y' : sy , 'body' : [] , 'header' : [] }

# Extract space separatated value array from file
def getdata_lines(old_lines,**kwargs):
	lines=copy.copy(old_lines)
	lines=clean_lines(remove_comments(lines,**kwargs))
	#print lines
	nl=len(lines)
	i=0
	#while ~len(nums(lines[i])) and i<(nl-1):
	#	i=i+1
	nc=len(nums(lines[i]))
	ar=zeros((nl,nc))
	n=0;
	for i,line in enumerate(lines):
		#print line
		nu=nums(line)
		l=len(nu)
		if l:
			ar[n,0:l]=nu
			n=n+1
	return ar[0:n,:],n,nc

def getdata(fname,**kwargs):
	try:
		lines=getlines(fname)
		return getdata_lines(lines,**kwargs)
	except:
		print('Could not load from file %s' %fname)
		return [],-1,-1

# Extract space separatated value array from file
def readnumsinlines(fname,**kwargs):
	lines=clean_lines(remove_comments(getlines(fname),**kwargs))
	br=[]
	for line in lines:
		nus=nums(line)
		if len(nus):
			br=append(br,nus[0])
	return br,len(br)

# Saves data from array
# todo : use **kwargs !
def savedata(*args,fname="default.txt",header="#",**kwargs):
	nargs=len(args)
	if nargs==0:
		return
	data=args[0]

	if nargs>1:
		fname=args[1]
		if nargs==3:
			header=args[2]

	fi=open(fname,'w')
	fi.write("%s \n" %(clean_line(header)))
	sha=shape(data)
	if len(sha)>1:
		if sha[0]>0 and sha[1]>0:
			fi.write("".join("".join((str(x)+" " for x in b))+"\n" for b in data))
	elif len(data)>0:
		fi.write("".join(str(b)+"\n" for b in data))
	fi.close()
	return

def savelines(lines,fname):
	f=open(fname,"w")
	for line in lines:
		f.write(line)
	f.close()
	return
