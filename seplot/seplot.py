# -*- coding: utf-8 -*-
#
# Copyright Serge Dmitrieff
# www.biophysics.fr
#
# Based on Python Pyx
"""
## SYNOPSIS

   seplot is a shorthand command-line/python tool to plot graphs using PyX. PyX is good.

## DESCRIPTION

   seplot plots a graph from text/csv files
   it is meant to be fast and dirty (but uses PyX to be beautiful)
   Can be used from the terminal (mostly) but also from a python script and notebook

## SYNTAX (from bash)

   seplot FILE [OPTIONS] [ADDITIONAL_FILES] [ADDITIONAL_OPTIONS]

## SYNTAX (from python)

    import seplot.seplot as sp
    plot=sp.Splotter([*args],[**kwargs])
    plot.add_plot([*args],[data=DATA],[file=FILENAME],[**kwargs])
    plot.make_and_save()
    # From a notebook :
    plot

## OPTIONS AND EXAMPLES

    See README.md and documentation

"""

from pyx import *
from numpy import *
from pyx.graph import axis
import sys
import sio_tools as sio

import seplot.kw_dictionaries as kd
import seplot.style_dictionaries as sd
from seplot.grapher import Graph


__VERSION__ = "2.2.5"




# Basic set of colours, symbols, and lines
csl=sd.get_colors_symbols_lines()
colours=csl['colours']
colour_strings=csl['colour_strings']
symbols=csl['symbols']
linests=csl['linests']
# dictionaries
dicos=sd.get_dictionaries()
col_dict=dicos['colors']
linst_dict=dicos['lines']
symst_dict=dicos['symbols']
linw_dict=dicos['widths']
grad_dict=dicos['gradients']
kw_dict=kd.get_keywords()

__SPLIT_MARK__ = '--split_mark--'

def version():
    return __VERSION__

class Toplot:
    """
    Toplot is a class containing the options for plotting
    it also contains a method to split into two
    here we need to support a keyword argument having to values, until we split
    therefore we don't convert everything to *args and **kwargs,
    rather we pass *argument*, a list of arguments and kw arguments

    """
    def __init__(self, *args, arguments=None, data=None, fname=None, **kwargs):
        """ Initialization"""
        self.fname=fname
        """ filename to read data from """
        self.data=data
        """ data to plot from """
        self.arguments=[]
        self.kwarguments={}
        """ actual arguments"""
        if arguments is not None:
            self.arguments=arguments
        self.arguments.extend((args))
        #for arg in args:
        #    self.arguments.append(arg)
        self.kwarguments.update(**kwargs)




    def check_split(self):
        """ Checking if we need to split the graph into several graphs when implied from arguments"""
        na=len(self.arguments)
        do_split=0
        for i,arg in enumerate(self.arguments):
            if arg==__SPLIT_MARK__:
                do_split=1
                n_split=i
        if do_split:
            #print('splitting with %s' %self.arguments)
            future_args=self.arguments
            future_kwargs=self.kwarguments
            self.arguments=self.arguments[0:n_split]
            future_args.pop(n_split)
            if len(future_args)>n_split:
                if future_args[n_split]=='-discard':
                    if len(future_args)>n_split+1:
                        future_args=future_args[(n_split+1):]
                    else:
                        future_args=[]

            new_dict={**self.__dict__}
            new_dict['arguments']=future_args
            new_dict.update(future_kwargs)
            #print('new object with : %s ' %(new_dict))
            return [1,Toplot(**new_dict)]
        else:
            return [0,1]

    def unpack_arguments(self):
        """ We convert our coarse list of arguments as a list of strings to a better arg / kwargs format"""

        _args = []
        _args.extend(self.arguments)

        _nextkwargs = {}
        _nextkwargs.update(self.kwarguments)

        _kwargs = {}

        # we may need to translate some arguments
        keys = kw_dict.keys()
        for arg in list(_args):
            if arg.find('=')>0:
                _args.remove(arg)
                largs=arg.split('=')
                # We fix weird /illegal syntax
                if largs[0] in keys:
                    largs[0]=kw_dict[largs[0]]
                try:
                    val='='.join(largs[1:])
                    _kwargs[largs[0]]=val
                except:
                    raise ValueError('Could not process argument %s' %arg)
        _kwargs.update(_nextkwargs)
        godel = []
        for key, item in _kwargs.items():
            if key in keys:
                godel.append(key)
        # cleaning up
        for key in godel:
            _kwargs[kw_dict[key]] = _kwargs[key]
            _kwargs.pop(key)

        # let's not forget filename and/or data
        if self.fname is not None:
            _kwargs['fname']=self.fname
        if self.data is not None:
            _kwargs['data']=self.data

        return _args,_kwargs




class Splotter:
    """
    Splotter is the global plotter class
    It mostly sorts arguments and prepares global plot options

    Arguments passed :
    - arguments=: a list of arguments and kw arguments (those include "=")
    - data= : an array/dataframe containing data to be plotted
    - *args : additional arguments
    - **kwargs : additional keyword arguments
    """
    def __init__(self,*args,arguments=None,data=None,fname=None, **kwargs):
        """ Initiation  from arguments and keyword arguments"""
        if arguments is None:
            arguments = []

        self.canvas = canvas.canvas()
        """ The canvas (see PyX) """

        self.graph = None
        """ The graph itself, an instance of PyX.graph.graphxy """

        self.out = 'plot'
        """ The name of the output file """

        self.xlabel = None
        """ xlabel """
        self.ylabel = None
        """ ylabel """
        self.xmin = None
        """ min value of x axis """
        self.xmax = None
        """ mas value of x axis """
        self.ymin = None
        """ min value of y axis """
        self.ymax = None
        """ max value of y axis """
        self.key = None
        """ position of the legend (string, cf PyX) """
        self.bgcolor = None
        """ background color """
        self.width = 8
        """ graph width """
        self.height = 5
        """ graph height"""
        self.kdist = 0.1
        """ distance of the legend"""
        self.xlog = 0
        """ if x axis in log scale """
        self.ylog = 0
        """ if y axis in log scale """
        self.autolabel = 0
        """ if we auto label axes """
        self.equalaxis = 0
        """ if axes are equal """

        self.future_plots=[]
        """ the list items to be plotted, """
        self.graphs=[]
        """ the list of created graphs """

        # Now we add extra arguments ; this is a bit weird but the simplest option to use both command line and python import
        for arg in args:
            arguments.append(arg)
        #for key, value in kwargs.items():
        #    arguments.append('%s=%s' %(key,value))

        xy_provided = False
        # Now we read arguments
        for key in kwargs.keys():
            if key=="x" or key=="y":
                xy_provided = True
        # and if we have data to plot we add it to future plots
        current_args = self.read_args(arguments=arguments, **kwargs)
        if data is not None:
            self.add_plot(data=data,arguments=current_args,  **kwargs)
        elif fname is not None:
            self.add_plot(fname=fname, arguments=current_args, **kwargs)
        elif xy_provided:
            self.add_plot(arguments=current_args,  **kwargs)


    # Integration with IPython (jupyter notebook) : png representation
    def _repr_png_(self):
        """ For ipython notebooks to display the graph """
        return self.canvas._repr_png_()

    # Integration with IPython (jupyter notebook) : svg representation
    def _repr_svg_(self):
        """ For ipython notebooks to display the graph """
        return self.canvas._repr_svg_()

    # Just a wrapper
    def add_plot(self,*args,**kwargs):
        """ a wrapper to add a plot to future_plots """
        self.future_plots.append(Toplot(*args,**kwargs))

    def read_args(self, *args, arguments=None, **kwargs):
        """ Where actually we read arguments !
        inputs :
        - arguments= : a list of arguments or kwarguments
        - *args : additional arguments
        - *kwargs : additional keyword arguments
        """

        if arguments is None:
            arguments = []
        ## Now we read arguments
        for arg in args:
            arguments.append(arg)
        for key, value in kwargs.items():
            if key.startswith('file='):
                # if the input is a file
                arguments.append(value)
            else:
                # for any other keyword argument
                arguments.append('%s=%s' %(key,value))
        keyz=''
        current_args=[]
        keep=0
        has_name=0
        fname=None
        # we iterate through arguments and assign them to global or local options
        for arg in arguments:
            # Global options
            if arg.startswith('out='):
                self.out=arg[4:]
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
                self.ymax=float(arg[5:])
            elif arg.startswith('bgcolor='):
                self.bgcolor=arg[8:]
            elif arg.startswith('key='):
                keyz=arg[4:]
            elif arg.startswith('-key') or arg.startswith('-legend'):
                keyz='tl'
            elif arg.startswith('kdist='):
                self.kdist=arg[6:]
            elif arg.startswith('legend=') or arg.startswith('title'):
                self.key=graph.key.key(pos="tl", dist=self.kdist)
                current_args.append(arg)
            elif arg.endswith('-help'):
                print("seplot version %s " %version())
                self.usage()
            elif arg.startswith('-autol'):
                self.autolabel=1
            elif arg.startswith('-equal'):
                self.equalaxis=1
            elif arg.startswith('-xlog'):
                self.xlog=1
            elif arg.startswith('-ylog'):
                self.ylog=1
            # Local / semi-local options
            elif arg.startswith('andif'):
                if has_name==0:
                    raise ValueError('Error : cannot use andif= before the first declared file')
                else:
                    #future_plots.append(Toplot(fname,current_args))
                    current_args.append(__SPLIT_MARK__)
                    current_args.append(arg)

            elif arg.startswith('-keep'):
                keep=1
            elif arg.startswith('-discard'):
                keep=0
            elif arg.startswith('function='):
                # If there is already a name for a future plot, we append the former to be created
                if has_name:
                    self.future_plots.append(Toplot(fname=fname,arguments=current_args))
                    if keep==0:
                        current_args=[]
                else:
                    has_name=1
                current_args.append(arg)
                fname=None
            elif arg.startswith('-') or arg.find('=')>=0:
                current_args.append(arg)
            # If it's not an option, it's definitey a filename
            elif arg=='and':
                current_args.append(__SPLIT_MARK__)
                if keep==0:
                    current_args.append('-discard')
            else:
                # If there is already a name for a future plot
                if has_name:
                    self.future_plots.append(Toplot(fname=fname,arguments=current_args))
                    if keep==0:
                        current_args=[]
                else:
                    has_name=1
                fname=arg
        # We still need add the last file to future_plots
        if has_name:
            self.future_plots.append(Toplot(fname=fname,arguments=current_args))
            has_name=0
        # also we check key position
        try:
            self.key=graph.key.key(pos="%s" %(keyz), dist=float(self.kdist))
        except:
            if keyz=='None':
                self.key=None
        # we return current arguments
        return current_args

    def make_and_save(self,*args,**kwargs):
        self.make_plot(*args,**kwargs)
        self.save_plot(*args,**kwargs)

    def make_plot(self,*args,**kwargs):
        """ We do the plotting by dispatching the arguments to PyX. Arguments can be passed again ! """
        self.read_args(*args,**kwargs)
        # we check if the plots must be split by and / andif

        for i,toplot in enumerate(self.future_plots):
            [is_split,new_plot]=toplot.check_split()
            if is_split:
                #print('splitting  ******************************')
                self.future_plots.append(new_plot)

        # We create the graphs
        for i,toplot in enumerate(self.future_plots):
            (args,kwargs)=toplot.unpack_arguments()
            kwargs['numr']=i
            self.graphs.append(Graph(*args,**kwargs))

        # Not a great option thou
        if self.autolabel:
            for graf in self.graphs:
                if graf.xlabel:
                    if not self.xlabel:
                        self.xlabel=graf.xlabel
                if graf.ylabel:
                    if not self.ylabel:
                        self.ylabel=graf.ylabel

        # we deal with global plot properties
        if self.xlabel:
            try:
                self.xlabel=r"%s" %(self.xlabel)
            except:
                self.xlabel=None

        if self.ylabel:
            try:
                self.ylabel=r"%s" %(self.ylabel)
            except:
                self.ylabel=None

        if self.equalaxis:
            self.height=self.width
            self.make_equal_axis_range()


        if self.xlog:
            xaxis=axis.log(title=self.xlabel,min=self.xmin,max=self.xmax);
            for graf in self.graphs:
                if sum(array(graf.X)<=0):
                    raise ValueError('Could not plot log with non-positive X values')
        else:
            xaxis=axis.linear(title=self.xlabel,min=self.xmin,max=self.xmax)

        if self.ylog:
            yaxis=axis.log(title=self.ylabel,min=self.ymin,max=self.ymax)
            for graf in self.graphs:
                if sum(array(graf.Y)<=0):
                    raise ValueError('Could not plot log with non-positive X values')
        else:
            yaxis=axis.linear(title=self.ylabel,min=self.ymin,max=self.ymax)

        backgroundattrs = None
        if self.bgcolor is not None:
            if self.bgcolor in col_dict.keys():
                backgroundattrs=[deco.filled([col_dict[self.bgcolor]])]
            else:
                if not self.bgcolor.startswith("color"):
                    if self.bgcolor.find(".")==-1:
                        self.bgcolor = "cmyk.%s" % self.bgcolor
                    self.bgcolor="color.%s" %self.bgcolor
                try:
                    backgroundattrs=[deco.filled([eval(self.bgcolor)])]
                except:
                    sio.custom_warn("Cound not understand background color from %s" %self.bgcolor)

        self.graph = graph.graphxy(width=self.width,height=self.height,key=self.key,
                                 backgroundattrs=backgroundattrs,
                                 x=xaxis,
                                 y=yaxis )

        ## Here we do the plotting itlsef
        for graf in self.graphs:
            self.plot(graf)
        ## We finish() the graph to be able to work with pathes
        self.graph.finish()
        #self.canvas.insert(self.graph)

        ## Now if there are graphs with a stroke_style, we paint them !
        # This is meant for histograms
        for graf in self.graphs:
            if len(graf.stroke_style):
                for plot in graf.ploted:
                    self.canvas.stroke(plot.path,graf.stroke_style)

        self.canvas.insert(self.graph)





    def plot(self,graf):
        """ A wrapper for PyX.graph.plot """
        if graf.is_function==1:
            graf.ploted=self.graph.plot(graph.data.function(graf.function_string,points=graf.n_points,title=graf.legend),graf.style)
        elif graf.is_histogram==1:
            graf.ploted=self.graph.plot([graph.data.points([(x,graf.Y[i]) for i, x in enumerate(graf.X[:])], x=1, y=2,title=graf.legend)],graf.style)
        else:
            graf.ploted=self.graph.plot([graph.data.points([(x,graf.Y[i],graf.dX[i],graf.dY[i],graf.S[i],graf.C[i]) for i, x in enumerate(graf.X[:])], x=1, y=2,dx=3,dy=4,size=5,color=6,title=graf.legend)],graf.style)

    def save_plot(self,*args,out=None,**kwargs):
        """ Saving canvas to a file """
        if not out:
            out=self.out
        if self.graphs:
            if out.endswith('.eps'):
                self.canvas.writeEPSfile(out)
            elif out.endswith('.svg'):
                self.canvas.writeSVGfile(out)
            else:
                self.canvas.writePDFfile(self.out)

    def make_equal_axis_range(self):
        xmax=None
        self.xmax=apply_on_not_none(self.xmax,self.ymax,function=max)
        self.xmin=apply_on_not_none(self.xmin,self.ymin,function=min)
        if self.xmin is None:
            (self.xmin,xmax)=self.get_data_extrema()
        if self.xmax is None:
            if xmax is not None:
                self.xmax=xmax
            else:
                (xmin,self.xmax)=self.get_data_extrema()
        self.ymax=self.xmax
        self.ymin=self.xmin

    def get_data_extrema(self):
        minv=sys.float_info.max
        maxv=-minv
        for graf in self.graphs:
            if not graf.is_function:
                minv=min(minv,min(graf.X),min(graf.Y))
                maxv=max(maxv,max(graf.X),max(graf.Y))
        return minv,maxv


    def usage(self):
        disp('seplot is a simple command line plotting tool based on PyX (PyX is awesome !)')
        disp('---------------------------- Warning : you should use PyX for more options')
        disp('Examples :')
        disp('seplot.py file.txt')
        disp('seplot.py file.txt color=red file2.txt out=plot.pdf')
        disp('seplot.py file.txt y=A[:,1]^2+A[:,2]^2 dy=3 color=1')
        quit


def apply_on_not_none(*args,function=None):
    nn=not_none(*args)
    if len(nn):
        return function(nn)
    else:
        return None

def not_none(*args):
    return [arg for arg in args if arg is not None]
