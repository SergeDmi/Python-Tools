# -*- coding: utf-8 -*-
import math
from numpy import *
import subprocess
import os.path
import sys


def modulo(k,n):
	c=0
	while k>=n:
		k=k-n
		c=c+1
	return k,c
# General tools Tools for
def make_exec(fname):
	return run("chmod +x "+fname)

#Runs a unic command and returns the stdout
def unpy(job):
	proc=subprocess.Popen([job],stdout=subprocess.PIPE)
	return proc.stdout.readlines() 

#pwd
def pwd():
	lines=unpy('pwd')
	return clean_line(lines[0])

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
# Remove / at the end of folder names
def clean_name(fname):
	l=len(fname)
	if l and fname.find("/")==l-1:
		return fname[0:l-1]
	else:
		return fname

# Remove commented lines / line sections
def remove_comments(lines):
	CC=["#","%"]
	for c in CC:
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
		
		
# Concatenate folder names, being carefull of the "/" at the end
def conc(*names):
	l=len(names)
	if l>1:
		return "%s/%s" % (clean_name(names[0]),conc(*names[1:l]))
	else:
		return names[0]

# Remove end-of-line (\n) for a string
def clean_line(line):
	#while line.find("\n")>-1:
	line=line.rstrip("\n")
	return line

# Remove end-of-lines (\n) for an array of strings
def clean_lines(lines):
	for i,line in enumerate(lines):
		lines[i]=clean_line(line)
	return lines
	
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
def write_file(folder_name,file_name,lines):
	fname=conc(folder_name,file_name)
	f=open(fname,'w')
	for line in clean_lines(lines):
		f.write(line+"\n")
	f.close()
	return

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
	
def getheader(fname):
	lines=clean_lines(getlines(fname))
	CC=["#","%"]
	line=""
	for c in CC:
		if lines[0].find(c)>=0:
			line=lines[0];
	return (line)
	
def splitheader(fname):
	head=getheader(fname)
	if head:
		return head.split(' ')
	else:
		return []
	
# Extract space separatated value array from file
def getdata_lines(lines):
	lines=clean_lines(remove_comments(lines))
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

def getdata(fname):
	lines=getlines(fname)
	return getdata_lines(lines)

# Extract space separatated value array from file
def readnumsinlines(fname):
	lines=clean_lines(remove_comments(getlines(fname)))
	br=[]
	for line in lines:
		nus=nums(line)
		if len(nus):
			br=append(br,nus[0])
	return br,len(br)

# Saves data from array
def savedata(*args):
	nargs=len(args)
	if nargs==0:
		return
	data=args[0]
	fname="default.txt"
	header="#"
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