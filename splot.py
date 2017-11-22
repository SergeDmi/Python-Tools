#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#import random,math
from pyx import *
from numpy import *
from pyx.graph import axis
from tools import *

		
class Glob:
	def __init__(self, args):
		narg=len(args)
		if nargs<2:
			self.usage()
		self.out='plot'
		self.xlabel='x'
		self.ylabel='y'
		self.xmin=None
		self.xmax=None
		self.ymin=None
		self.ymax=None
		self.key='tl'
		self.width=8
		self.height=5
		files=[]
		for i,arg in enumerate(args):
			if arg.startswith('out='):
				self.out=arg[5:]
			elif arg.startswith('xlabel='):
				self.xlabel=arg[7:]	
			elif arg.startswith('ylabel='):
				self.ylabel=arg[7:]	
			elif arg.startswith('width='):
				self.width=float(arg[6:])
			elif arg.startswith('height='):
				self.height=float(arg[7:])
			elif arg.startswith('xmin='):
				self.xmin=float(arg[5:])
			elif arg.startswith('ymin='):
				self.ymin=float(arg[5:])
			elif arg.startswith('xmax='):
				self.xmax=float(arg[5:])
			elif arg.startswith('ymax='):
				self.xmax=float(arg[5:])
			elif arg.startswith('key='):
				self.key=arg[4:]
			elif arg.startswith('--help'):	
				self.usage()
			elif arg.find('=')<0:
				files.append(i)		
				
		self.graph=graph.graphxy(width=self.width,height=self.height,key=graph.key.key(pos="%s" %(self.key), dist=0.1),x=axis.linear(title=r"%s" %(self.xlabel),min=self.xmin,max=self.xmax),y=axis.linear(title=r"%s" %(self.ylabel),min=self.ymin,max=self.ymax))		
		files.append(narg)
		nf=len(files)-1
		self.graphs=[Graph(args[files[i]:files[i+1]]) for i in range(nf)]
	def make_plot(self):
		for graf in self.graphs:
			self.plot(graf)	
	def plot(self,graf):
		if not graf.dy:
			self.graph.plot([graph.data.points([(x,graf.data[i,1]) for i, x in enumerate(graf.data[:,0])], x=1, y=2,title=graf.legend)],graf.style)
		else:
			self.graph.plot([graph.data.points([(x,graf.data[i,1],graf.data[i,2]) for i, x in enumerate(graf.data[:,0])], x=1, y=2,dy=3,title=graf.legend)],graf.style)
	def save_plot(self):
		if self.graphs:
			self.graph.writePDFfile(self.out)		
			self.graph.writeEPSfile(self.out)	

	def usage(self):
		disp('splot is a simple command line plotting tool based on PyX (PyX is awesome !)')
		disp('---------------------------- Warning : you should use PyX for more options')
		disp('Examples :')
		disp('splot.py positions.txt')
		disp('splot.py positions.txt positions2.txt')
		disp('splot.py positions.txt legend=None color=red averages.txt dy=2 style=x xlabel=''$t$ in minutes'' ylabel=''$\bar{z}$''')
		quit
			
class Graph(Glob):
	count=0
	numr=0
	def __init__(self, args):
		self.numr+=1
		self.x=0
		self.y=1
		self.mode='v'
		self.file=args[0]
		self.legend="file %s" %self.numr
		self.data=[]
		self.style=Style(args).style
		self.dy=[]		
		(a_exp,a,b)=getdata(self.file)
		labels=splitheader(self.file)
		
		self.data=a_exp
		
		for arg in args:
			if arg.startswith('legend='):
				legend=arg[7:]
				if legend=='None' or legend=='none':
					self.legend=None
				else:
					self.legend=r"%s" %legend
			elif arg.startswith('x='):
				self.x=int(arg[2:])	
			elif arg.startswith('y='):
				self.y=int(arg[2:])
			elif arg.startswith('mode='):
				self.mode=arg[5:]
			elif arg.startswith('dy='):
				self.dy=int(arg[3:])	
		if self.mode=='h':
			self.data=self.data.T
		if not self.dy:
			self.data=self.data[:,[self.x,self.y]]
		else:
			self.data=self.data[:,[self.x,self.y,self.dy]]
		
class Style(Graph):
	def __init__(self, args):
		count=Graph.count
		self.colour=color.gray(0.25*float(count %4))
		self.size=0.04+0.01*float(count %6)
		self.line=style.linewidth.thin
		self.style=[]
		self.dy=[]
		
		for arg in args:
			if arg.startswith('color='):
				col=arg[6:]
				if col=='red':
					self.colour=color.rgb.red
				elif col=='blue':
					self.colour=color.rgb.blue
				elif col=='green':	
					self.colour=color.rgb.green
				elif col=='light':						
					self.colour=color.gray(0.75)					
				elif col=='medium':						
					self.colour=color.gray(0.5)					
				elif col=='dark':
					self.colour=color.gray(0.25)					
			elif arg.startswith('size='):
				self.size=float(arg[5:])
				
			elif arg.startswith('line='):
				lin=int(arg[5:])
				if lin==0:
					self.line=style.linewidth.thin
				elif lin==1:
					self.line=style.linewidth.thick
				elif lin==2:
					self.line=style.linewidth.Thick
				elif lin==3:
					self.line=style.linewidth.THick
				elif lin==4:
					self.line=style.linewidth.THIck
				elif lin==5:
					self.line=style.linewidth.THICK
					
			elif arg.startswith('dy='):
				self.dy=int(arg[3:])
				
		for arg in args:	
			if arg.startswith('style='):		
				stil=arg[6:]
				if stil=='_' or stil=='-':
					self.style=[graph.style.line([style.linestyle.solid,self.line,self.colour])]
				elif stil=='--':
					self.style=[graph.style.line([style.linestyle.dashed,self.line,self.colour])]
				elif stil=='.-':
					self.style=[graph.style.line([style.linestyle.dashdotted,self.line,self.colour])]
				elif stil=='x':
					if not self.dy:
						self.style=[graph.style.symbol(graph.style.symbol.cross, size=self.size,symbolattrs=[deco.stroked([self.colour])])]
					else:
						self.style=[graph.style.symbol(graph.style.symbol.cross, size=self.size,symbolattrs=[deco.stroked([self.colour])]),graph.style.errorbar(errorbarattrs=[self.line,self.colour])]  
				elif stil=='o':
					if not self.dy:
						self.style=[graph.style.symbol(graph.style.symbol.circle, size=self.size,symbolattrs=[deco.stroked([self.colour])])]    	
					else:
						self.style=[graph.style.symbol(graph.style.symbol.circle, size=self.size,symbolattrs=[deco.stroked([self.colour])]),graph.style.errorbar(errorbarattrs=[self.line,self.colour])]  
					
		if not self.style:
			Graph.count+=1
			if not self.dy:
				self.style=[graph.style.symbol(graph.style.symbol.cross, size=self.size,symbolattrs=[deco.stroked([self.colour])])]
			else:
				self.style=[graph.style.symbol(graph.style.symbol.cross, size=self.size,symbolattrs=[deco.stroked([self.colour])]),graph.style.errorbar(errorbarattrs=[self.line,self.colour])]  

		
if __name__ == "__main__":
	nargs=len(sys.argv);
	args=sys.argv[1:];

	glob=Glob(args)
	glob.make_plot()
	glob.save_plot()

