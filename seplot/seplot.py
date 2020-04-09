#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright Serge Dmitrieff
# www.biophysics.fr
#
# Based on Python Pyx
from pyx import *
from numpy import *
from pyx.graph import axis
import sys
import sio_tools as sio
import copy

if __package__:
    import seplot.kw_dictionaries as kd
    import seplot.style_dictionaries as sd
else:
    import kw_dictionaries as kd
    import style_dictionaries as sd


__VERSION__ = "2.0.1"

"""
# SYNOPSIS

   seplot is a shorthand command-line tool draw graphs using PyX. PyX is good.

# DESCRIPTION

   seplot plots a graph from a text file (should I add excel support ?)
   it is meant to be fast and dirty (but uses PyX to be beautiful)

# SYNTAX

   python seplot.py TEXT_FILE [OPTIONS] [ADDITIONAL_TEXT_FILES] [ADDITIONAL_OPTIONS]

# OPTIONS

    seplot has two kinds of options : global (for the whole figure) and local (for a particular file)
    All options should be written as option_name=option_value

    Global options :
        xlabel        : label of x axis
        ylabel        : label of y axis
        width         : width of figure
        height        : height of figure
        xmin          : min x value
        xmax          : max x value
        ymin          : min y value
        ymax          : max y value
        key           : position of figure legend (tr,br,tl,bl)
        out           : name of output file
        -ylog         : y axis is logarithmic
        -xlog         : x axis is logarithmic
        -keep         : keep options for subsequent plots, until -discard
        -discard      : discard options for next plot
        -equal        : equal x-y axis range
        -autolabels   : tries to automatically find labels from data file

    Local options :
        x        : index of column or row to be used as x axis values (e.g. x=0 for the first column)
                        also can specify a label read from file header : x=column_label
                        also can specify an operation : x='A[:,0]*A[:,1]' or x='column_label*column_label'
                        can also be automatic, i.e. index : x=auto
        y        : index of column or row to be used as y axis values, same possibilities as x=
        dy       : index of column or row to be used as dy values , same possibilities as x=
        mode     : h for horizontal (rows), v for vertical (column) (default)

        color    : color of lines or symbol ; can be either red, green, blue, dark, medium, light, black
                        or color.cmyk.*  or color.rgb.*
                        or an operation, e.g. color=A[:,2] or color=columns_label*5

        and      : add another graph (possibly with different options)

        style    : style of plot : - or _ for a line, -- for dashed, .- for dashdotted
                                    o for circles  x , * for crosses  + for plus   > , <     for triangles
                                    b for a bar graph , B for a filled bar graph (histogram)

        if / cond : condition to keep the rows or columns

        andif     :  add another graph with different conditions

        range    : range of rows / columns to plot

        size     : size of symbol used

        line     : thickness of line, from 0 to 5

        title (or legend) : title of the graph

        -hist    : makes a histogram out of the data

# EXAMPLES :

            seplot.py file.txt
                        plots the second column of file.txt as a function of the first column
            seplot.py file.txt x=3 y=7
                        plots the 4th (3+1) column of file.txt as a function of the eigth column (7+1)
            seplot.py file.txt x=3 y=7 and x=3 y=10
                        plots the 4th (3+1) column of file.txt as a function of the eigth column (7+1),
                        and another plot of 4th column as a function of 11th column
            seplot.py file.txt color=red file2.txt out=plot.pdf
                        plots in red the second column of file.txt as a function of the first column
                        plots the second column of file2.txt as a function of the first column in the same graph
            seplot.py file.txt 'y=sqrt(A[:,1]^2+A[:,2]^2)' dy=3 color=1 grad=gray xlabel='$t$ in minutes' ylabel='$\bar{z}$'
                        A[:,1] and A[:,2] are the second and third columns of file.txt
                        the deviation is set from the fourth column of file.txt
                        the color is set from the second column of file.txt, based on a gray-level gradient
                        labels and titles use the Latex interpreter
            seplot.py file.txt if='x>1'
                        plots the second column as a function of the first if elements of the first are greater than 1
            seplot.py file.txt mode='h' if='A[0,:]>1' -xlog
                        plots the second row as a function of the first row if elements of the first row are greater than 1
                        the x axis is logarithmic
            seplot.py file.txt mode='h' if='x>1' andif='x<=1'
                        plots the second row as a function of the first row if elements of the first row are greater than 1
                        and (with a different style) if the elements of the first row are smaller than 1
            seplot.py range=3 -keep data_0*.txt
                        plots data from only the third line of the files data_0*.txt
            seplot.py file.txt range=0:4
                        plots data from only the first to 4th line of file.txt
            seplot.py data.txt x=1 y=2 and y=3
                        plots the third and fourth column as a function of the second

# USE seplot from python :
            # Single plot :
            import seplot
            plot=seplot.Splotter('-xlog',key='tr',data=A)           # A is a data array, arguments is a list of argument
            plot.make_and_save()                           # e.g. : arguments=['color=red','-xlog']
            # Several plots :
            plot=seplot.Splotter('-autolabel',key='tl')
            plot.add_plot(data=A,color='blue')
            plot.add_plot(data=B,color=red)
            plot.make_and_save()

"""

#@TODO :    yaml config file
#@TODO :    separate script from module !


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

def get_histogram(Y,bins='auto'):
    (Y,X)=histogram(Y,bins)
    nx=len(X)
    if nx:
        X=(X[0:(nx-1)]+X[1:nx])/2.0
    else:
        raise ValueError('Empty histogram from numpy.histogram')
    return (Y,X)

class Toplot:
    # Toplot is a class containing the options for plotting
    #   it also contains a method to split into two
    # here we need to support a keyword argument having to values, until we split
    # therefore we don't convert everything to *args,**kwargs for now
    # @TODO : toplot should have a kwarg member ! -> No need to translate
    def __init__(self,*args,arguments=[],data=[],fname="",**kwargs):
        self.fname=fname
        self.data=data
        self.arguments=[arg for arg in arguments]
        for arg in args:
            self.arguments.append(arg)
        for key, value in kwargs.items():
            self.arguments.append('%s=%s' %(key,value))

    def check_split(self):
        na=len(self.arguments)
        do_split=0
        for i,arg in enumerate(self.arguments):
            if arg==__SPLIT_MARK__:
                do_split=1
                n_split=i
        if do_split:
            #print('splitting with %s' %self.arguments)
            future_args=self.arguments
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
            #print('new object with : %s ' %(new_dict))
            return [1,Toplot(**new_dict)]
        else:
            return [0,1]

    def unpack_arguments(self):
        # We convert our stupid list of arguments as a list of strnigs to a better arg / kwargs format
        args=self.arguments
        kwargs={}
        keys=kw_dict.keys()
        for arg in list(args):
            if arg.find('=')>0:
                args.remove(arg)
                largs=arg.split('=')
                # We fix weird /illegal syntax
                if largs[0] in keys:
                    largs[0]=kw_dict[largs[0]]
                try:
                    val='='.join(largs[1:])
                    kwargs[largs[0]]=val
                except:
                    raise ValueError('Could not process argument %s' %arg)
        # let's not forget filename and/or data
        kwargs['fname']=self.fname
        kwargs['data']=self.data
        return args,kwargs




class Splotter:
    # seplot is the global plotter class
    # It mostly sorts arguments and prepares global plot options
    def __init__(self,*args,arguments=[],data=[],**kwargs):
        ## First we initialize class members
        self.canvas=canvas.canvas()
        #if not args and not data:
        #    self.usage()
        self.out='plot'
        self.xlabel=None
        self.ylabel=None
        self.xmin=None
        self.xmax=None
        self.ymin=None
        self.ymax=None
        self.key=None
        self.width=8
        self.height=5
        self.kdist=0.1
        self.xlog=0
        self.ylog=0
        self.autolabel=0
        self.equalaxis=0
        self.future_plots=[]
        self.graphs=[]
        data=array(data)
        # Now we add extra arguments ; this is a bit weird but the simplest option to use both command line and python import
        for arg in args:
            arguments.append(arg)
        for key, value in kwargs.items():
            arguments.append('%s=%s' %(key,value))
        # Now we read arguments
        current_args=self.read_args(arguments=arguments)
        # and if we have data to plot we add it to future plots
        if data.size>0:
            self.add_plot(data=data,arguments=current_args)

    # Just a wrapper
    def add_plot(self,*args,**kwargs):
        self.future_plots.append(Toplot(*args,**kwargs))

    def read_args(self,*args,arguments=[],**kwargs):
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
        fname=''
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
                fname=''
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
        self.read_args(*args,**kwargs)
        # we check if the plots must be split by and / andif
        for i,toplot in enumerate(self.future_plots):
            [is_split,new_plot]=toplot.check_split()
            if is_split:
                #print('splitting  ******************************')
                self.future_plots.append(new_plot)

        ## Now we create the graphs
        # We create the graphs
        #self.graphs=[Graph(toplot) for toplot in self.future_plots]
        for i,toplot in enumerate(self.future_plots):
            (args,kwargs)=toplot.unpack_arguments()
            kwargs['numr']=i
            self.graphs.append(Graph(*args,**kwargs))

            #print(i)
        #self.graphs=[Graph(toplot) for toplot in self.future_plots]
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


        self.graph=graph.graphxy(width=self.width,height=self.height,key=self.key,
                x=xaxis,
                y=yaxis )

        ## Here we do the plotting itlsef
        for graf in self.graphs:
            self.plot(graf)
        ## We finish() the graph to be able to work with pathes
        self.graph.finish()

        ## Now if there are graphs with a stroke_style, we paint them !
        # This is meant for histograms
        for graf in self.graphs:
            if len(graf.stroke_style):
                for plot in graf.ploted:
                    self.canvas.stroke(plot.path,graf.stroke_style)

        self.canvas.insert(self.graph)




    def plot(self,graf):
        if graf.is_function==1:
            graf.ploted=self.graph.plot(graph.data.function(graf.function_string,points=graf.n_points,title=graf.legend),graf.style)
        elif graf.is_histogram==1:
            #print(graph.X)
            graf.ploted=self.graph.plot([graph.data.points([(x,graf.Y[i]) for i, x in enumerate(graf.X[:])], x=1, y=2,title=graf.legend)],graf.style)
            #self.graph.plot([graph.data.points([(x,graf.Y[i]) for i, x in enumerate(graf.X[:])], xname=1, y=2,title=graf.legend)],graf.style)
            #self.graph.plot([graph.data.points([(x,graf.Y[i]) for i, x in enumerate(graf.X[:])],xname=0, y=2,title=graf.legend)],[graph.style.changebar()])
        else:
            graf.ploted=self.graph.plot([graph.data.points([(x,graf.Y[i],graf.dX[i],graf.dY[i],graf.S[i],graf.C[i]) for i, x in enumerate(graf.X[:])], x=1, y=2,dx=3,dy=4,size=5,color=6,title=graf.legend)],graf.style)

    def save_plot(self,*args,out=None,**kwargs):
        if not out:
            out=self.out
        if self.graphs:
            if out.endswith('.eps'):
                self.canvas.writeEPSfile(out)
            elif out.endswith('.svg'):
                self.canvas.writeSVGfile(out)
            else:
                #self.graph.writePDFfile(self.out)
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

class Graph(Splotter):
    # Graph is a class containing a single line/set of points and their style, created from class Toplot
    def __init__(self,*args,
                x=0,y=1,dx=[],dy=[],col='',siz='',stil='',
                cond=[],range=[],
                function_string='',legend='',
                fname='',data=[],numr=0,mode='v',
                n_points='200',
                **kwargs):

        self.fname=fname ; self.function_string=function_string
        self.data=array(data)
        self.numr=numr
        self.mode=mode ; self.numr=numr
        self.dX=[] ; self.dY=[]
        self.X=[] ; self.Y=[] ; self.S=[] ; self.C=[]
        self.is_function=0
        self.is_histogram=0
        self.make_histogram=0
        self.xlabel=None ; self.ylabel=None
        self.labels=[]
        self.range=range
        self.set_n_points(n_points)
        self.label_dict={}
        self.color_from_data=False
        self.legend=None
        self.path=None
        self.stroke_style=None

        self.make_auto_legend(legend)

        if self.function_string:
            self.is_function=1

        elif self.data.size>0:
            A=self.data
        else:
            in_data=sio.data_import_wrapper(self.fname)
            A=in_data['data']

            # Dirty tricks for maximum compatibility
            if min(in_data['size_x'],in_data['size_y'])==1:
                self.x='auto'
                self.y=0
            if in_data['size_x']==1:
                self.mode='h'

            # This is if we are dealing with (hopefuly) numeric data

            labels=in_data['labels']
            if self.mode=='v':
                ncols=A.shape[1]
            else:
                ncols=A.shape[0]

            if len(labels)<=ncols:
                self.labels=in_data['labels']
            #print(self.labels)
            for i,label in enumerate(self.labels):
                self.label_dict[label]=i

        # using local options
        #for arg in args:
        #    if arg.startswith('-hist'):
        #        self.is_histogram=1
        # There should be a style : bar

        # using local options
        for arg in args:
            if arg.startswith('-hist'):
                self.is_histogram=1
                self.make_histogram=1
                if not stil:
                    stil='B'
                elif not (stil=='b' or stil=='B'):
                    sio.custom_warn('Forcing style to histogram')


        if not self.is_function:
            if not self.make_histogram:
                # This is if we are dealing with (hopefuly) numeric data
                #if (len(self.range) or len(cond)):
                if len(range):
                    A=self.set_A_range(A,range)
                # Set X Y to start with
                self.set_init_XY(A)
                # We perform a first extraction of X and Y to be able to evalyate conditions on X,Y
                self.X=self.set_from_input(A,x,'x')
                self.Y=self.set_from_input(A,y,'y')
                self.dX=self.set_from_input(A,dx,'dx')
                self.dY=self.set_from_input(A,dy,'dy')

                #if (len(self.range) or len(cond)):
                if len(cond):
                    A=self.set_A_condition(A,cond)
                # Set X Y to start with
                self.set_init_XY(A)
                # Now we perform the definitive extraction of X,Y once A has been filtered
                self.X=self.set_from_input(A,x,'x')
                self.Y=self.set_from_input(A,y,'y')
                self.dX=self.set_from_input(A,dx,'dx')
                self.dY=self.set_from_input(A,dy,'dy')

                # Now we assign colors and size if need be
                #if siz.isdigit() or siz.find('A[')>=0:
                self.S=self.set_from_input(A,siz,'size')
                #if col.isdigit() or col.find('A[')>=0:
                self.C=self.set_from_input(A,col,'color')
                if len(self.C):
                    if not std(self.C)<sys.float_info.epsilon:
                        self.color_from_data=True
                    else:
                        sio.custom_warn("No variance in color provided, using random color based on mean value !")
                        col=colour_strings[int(mean(self.C)) %7]
                        self.C=[]
                    #print("Set color from data")

            else:
                # We're making a histogram !
                self.X=self.set_from_input(A,y,'y')
                if len(cond):
                    A=self.set_A_condition(A,cond)
                self.Y=self.set_from_input(A,y,'y')
                bin_number=0
                try:
                    bin_number=int(x)
                    if not bin_number==0:
                        try:
                            (self.Y,self.X)=get_histogram(self.Y,bins=bin_number)
                        except:
                            raise ValueError('Could not make histogram with data Y=%s and bins=%s (assumed bin number)'  %(y,x) )
                    else:
                        (self.Y,self.X)=get_histogram(self.Y,bins='auto')
                except:
                    try:
                        bins=sio.make_array_from_str(x)
                        #print(bins)
                        if len(bins):
                            try:
                                #(self.Y,self.X)=get_histogram(self.Y,bins=bins)
                                (self.Y,self.X)=histogram(self.Y,bins)
                            except:
                                raise ValueError('Could not make histogram with data Y=%s and bins=%s (assumed array)'  %(y,bins) )
                    except:
                        try:
                            (self.Y,self.X)=get_histogram(self.Y,bins=x)
                        except:
                            raise ValueError('Could not make histogram with data Y=%s and bins=%s (assumed text or other)'  %(y,x) )
                #print(self.X)
                #print(self.Y)

            try:
                if not len(self.C):
                    self.C=self.X
            except:
                self.C=self.X

            try:
                if not len(self.S):
                    self.S=self.X
            except:
                self.S=self.X

            # We check size
            lX=len(self.X)
            lY=len(self.Y)
            if lX>lY:
                self.X=self.X[0:lY]
                lX=lY
            elif lY>lX:
                self.Y=self.Y[0:lX]
                lY=lX
            if not len(self.dY):
                self.dY=zeros((lX,1))
            if not len(self.dX):
                self.dX=zeros((lX,1))

            # we scale the color scale
            self.C=(self.C-min(self.C))/(max(self.C)-min(self.C))

            # we make sure no size is non-positive
            if min(self.S)<=0:
                self.S=(self.S-min(self.S))+0.001

        # and now we can make the style !
        kwargs['col']=col ; kwargs['siz']=siz ; kwargs['is_function']=self.is_function
        kwargs['numr']=self.numr ; kwargs['dx']=dx ; kwargs['dy']=dy ; kwargs['stil']=stil
        kwargs['color_from_data']=self.color_from_data
        #kwargs['is_histogram']=self.is_histogram

        style=Style(*args,**kwargs)
        self.style=style.style
        self.stroke_style=style.stroke_style

        if style.goodstyle.kind=='histogram':
            self.is_histogram=1

        #if self.is_histogram:
            #self.stroke=Style(*args,**kwargs).style
            #self.stroke_style=style.stroke_style

             #self.stroke_style=Style(*args,**kwargs.style)

    def make_auto_legend(self,legend):
        if legend=='None' or legend=='none':
            self.legend=None
        elif legend:
            self.legend=r"%s" %legend
        else:
            if self.function_string:
                self.legend=self.function_string
            elif self.fname:
                lenf=len(self.fname)
                if lenf<=16:
                    self.legend=self.fname
            else:
                self.legend=None

    def set_init_XY(self,A):
        try:
            if self.mode=='h':
                self.X=A[0,:]
                self.Y=A[1,:]
            else:
                self.X=A[:,0]
                self.Y=A[:,1]
        except:
            sio.custom_warn('Could not set initial X Y values before reading arguments')
        return

    def set_n_points(self,arg):
        self.n_points=200
        try:
            self.n_points=int(arg)
        except:
            raise ValueError('Did not understand npoints from input %s'  %arg)

    # set a label for coordinate x or y
    def set_label(self,label,coord):
        if coord=='x':
            self.xlabel=label
        elif coord=='y':
            self.ylabel=label
        return

    def set_from_input(self,A,input,coord):
        # We first check if axis defined by a row/column number
        X=self.X;x=X
        Y=self.Y;y=Y

        if input in self.labels:
            input=self.label_dict[input]

        try :
            i=int(input)
            if self.mode=='h':
                # We try auto-setting the label if no label is defined
                if i<len(self.labels):
                    self.set_label(self.labels[i],coord)
                return A[i,:]
            else:
                if i<len(self.labels):
                    self.set_label(self.labels[i],coord)
                return A[:,i]
        except:
            if input:
                # Automatic axis value : 1 to length of array
                if input.startswith('aut'):
                    if self.mode=='h':
                        return array(range(len(A[0,:])))
                    else:
                        return array(range(len(A[:,0])))
                # Interpreting axis value
                for label in self.labels:
                    # trying to substitute label to array values
                    if input.find(label)>=0:
                        input=self.substitute_label(input,A,label)
                try:
                    return eval(input)
                except:
                    if not coord=="color":
                        raise ValueError('We could note evaluate %s from %s' %(coord,input))
                    else:
                        sio.custom_warn('We might not be able to evaluate %s from %s' %(coord,input))
                    return []
            else:
                return []

    def substitute_label(self,input,A,label):
        i=self.label_dict[label]
        if self.mode=='h':
            replace='A[%s,:]' %i
        else:
            replace='A[:,%s]' %i
        return input.replace(label,replace)

    def set_A_range(self,A,in_range):
        # first we need to make data horizontal for the range operation
        if self.mode=='h':
            B=A.transpose()
        else:
            B=A.copy()
        if len(in_range)>0:
            srange=in_range.split(":")
            lr=len(srange)
            try :
                iii=array([int(s) for s in srange])
                if lr==1:
                    B=array([B[iii[0]]])
                elif lr==2:
                    B=B[iii[0]:iii[1]]
                elif lr==3:
                    B=B[iii[0]:iii[2]:iii[1]]
                else:
                    #print('Range must be of the format begin:end or begin:range')
                    raise ValueError('Range must be of the format begin:end or begin:step:end')
            except:
                raise ValueError('Cannot convert Range to adequate format (note : range must be of the format begin:end or begin:step:end)')
        if self.mode=='h':
            A=B.transpose()
        else:
            A=B.copy()

        return A


    def set_A_condition(self,A,cond):
        if self.mode=='h':
            B=A.transpose()
        else:
            B=A.copy()

        if len(cond)>0:
            X=self.X;x=X
            Y=self.Y;y=Y
            try:
                kept=eval(cond)
                if self.mode=='h':
                    B=B[kept]
                    A=B.transpose()
                else:
                    A=A[kept]
            except:
                raise ValueError('Cannot understand condition. Hint use : if=\'A[:,2]>0.5\' ')

        return A

class Style(Graph):
    # A class containing the style to make a graph
    def __init__(self, *args,numr=0,
                dx=[],dy=[],
                **kwargs):

        self.style=[]
        self.dxy=[]
        self.stroke_style=[]
        if numr:
            kwargs['numr']=numr
        self.goodstyle=goodstyle(*args,**kwargs)
        #print(self.goodstyle.kind)
        #self.is_histogram=0

        #for arg in args:
        #    if arg.startswith('-hist') or arg.startswith('-makehist'):
        #        self.is_histogram=1

        if self.goodstyle.kind=='histogram':
            self.is_histogram=1
        #print(self.goodstyle.setcolor)
        if len(dx)>0 or len(dy)>0:
            if self.goodstyle.setcolor:
                self.dxy=[self.goodstyle.linew,self.goodstyle.setcolor]
            else:
                self.dxy=[self.goodstyle.linew,colours[0]]

        if self.goodstyle.kind=='symbol':
            symbol_dict={**vars(self.goodstyle)}
            symbol_dict['numr']=numr
            if not len(self.dxy):
                self.style=[changesymbol(**symbol_dict),graph.style.errorbar(False)]
            else:
                self.style=[changesymbol(**symbol_dict),graph.style.errorbar(errorbarattrs=self.dxy)]

        elif self.goodstyle.kind=='line':
            if not len(self.dxy):
                self.style=[graph.style.line([self.goodstyle.linest,self.goodstyle.linew,self.goodstyle.setcolor]),graph.style.errorbar(False)]
            else:
                self.style=[graph.style.line([self.goodstyle.linest,self.goodstyle.linew,self.goodstyle.setcolor]),graph.style.errorbar(errorbarattrs=self.dxy)]

        elif self.goodstyle.kind=='histogram':
            #self.style=[graph.style.bar()]
            self.style=[graph.style.histogram(lineattrs=[self.goodstyle.linew,self.goodstyle.setcolor],fillable=1)]

            self.stroke_style=self.goodstyle.stroke_style


class goodstyle(Style):
    # A class containing the style attributes to pass to python PyX
    def __init__(self,*args,
                numr=0,
                col='',siz='',line='',stil='',gradient='',
                is_function=0,color_from_data=False,
                **kwargs):

        self.kind='symbol'
        self.setcolor=colours[int(ceil(numr/4)) %4]
        self.symbol=symbols[numr %4]
        self.setsize=0.5
        self.linew=style.linewidth.thin
        self.linest=linests[numr %4]
        self.gradient=color.gradient.Rainbow;
        self.stroke_style=[]

        # By default, function should be a line
        #for arg in args:
        if is_function:
            self.kind='line'

        if col and not color_from_data:
            try :
                # We first try to set it from the dictionary
                self.setcolor=col_dict[col]
            except :
                if not col.startswith('color.'):
                    # shorthand notation is tolerated
                    col='color.%s' %(col)
                try:
                    # trying if color is a defined PyX color
                    self.setcolor=eval(col)
                except:
                    sio.custom_warn('Could not understand color from %s' %col)
        elif color_from_data:
            self.setcolor=None

        if gradient:
            try :
                # We first try to set it from the dictionary
                self.gradient=grad_dict[gradient]
            except :
                if not grad.startswith('color.gradient'):
                    # shorthand notation is tolerated
                    if grad.startswith('gradient'):
                        grad='color.%s' %(gradient)
                    else:
                        grad='color.gradient.%s' %(gradient)
                try:
                    # trying if color is a defined PyX color
                    self.gradient=eval(gradient)
                except:
                    sio.custom_warn('Could not understand gradient from %s' %gradient)

        if siz:
            if siz.find('A[')>=0:
                # Size depends on data
                self.setsize=-1
            else:
                try:
                    sizi=float(siz)
                    if siz.find('.')<0:
                        # size is a data column
                        self.setsize=-1
                    else:
                        # size is a numerical value
                        self.setsize=sizi
                except:
                    sio.custom_warn('Could not understand size from %s' %siz)

        if line:
            self.kind='line'
            if line.find('.')>=0:
                try:
                    self.linew=style.linewidth(float(line))
                except:
                    sio.custom_warn('Could not understand line width from %s' %line)
            else:
                try:
                    self.linew=linw_dict[line]
                except:
                    sio.custom_warn('Could not understand line width from %s' %line)

        if stil:
            if stil.startswith('b') or stil.startswith('B'):
                self.kind='histogram'
            else:
                try:
                    self.linest=linst_dict[stil]
                    self.kind='line'
                except:
                    try:
                        self.symbol=symst_dict[stil]
                        self.kind='symbol'
                    except:
                        sio.custom_warn('Could not understand style from %s' %stil)

        if not self.kind=='symbol':
            # For now seplot does not support gradient line coloring
            if not self.setcolor:
                self.setcolor=colours[int(ceil(numr/4)) %4]

        if is_function==1:
            if self.kind=='symbol':
                raise ValueError('Cannot use symbols with function. For point-valued function estimation please use x=A[:,i] y=function(A[:,j])')

        if stil:
            if stil.startswith('B'):
                self.stroke_style=[deco.filled([self.setcolor])]

class changesymbol(graph.style.symbol):
    # A flexible symbol class derived from PyX's very own changesymbol class
    def __init__(self,
                       sizecolumnname="size", colorcolumnname="color",
                       gradient=color.gradient.Rainbow,
                       symbol=graph.style.symbol.triangle,
                       symbolattrs=[deco.filled, deco.stroked],
                       setsize=0.5,kind='symbol',linew=False,linest=False,
                       setcolor=color.gray(0.0),numr=0,stroke_style=None,
                       **kwargs):
        # add some configuration parameters and modify some other
        self.sizecolumnname = sizecolumnname
        self.colorcolumnname = colorcolumnname
        self.gradient = gradient
        self.setsize = setsize
        self.setcolor = setcolor
        if self.setcolor:
            symbolattrs=[deco.filled([self.setcolor]), deco.stroked([self.setcolor])]
        graph.style.symbol.__init__(self, symbol=symbol, symbolattrs=symbolattrs, **kwargs)

    def columnnames(self, privatedata, sharedata, agraph, columnnames, dataaxisnames):
        # register the new column names
        if self.sizecolumnname not in columnnames:
            raise ValueError("column '%s' missing" % self.sizecolumnname)
        if self.colorcolumnname not in columnnames:
            raise ValueError("column '%s' missing" % self.colorcolumnname)
        return ([self.sizecolumnname, self.colorcolumnname] +
                graph.style.symbol.columnnames(self, privatedata, sharedata, agraph,
                                               columnnames, dataaxisnames))

    def drawpoint(self, privatedata, sharedata, graph, point):
        # replace the original drawpoint method by a slightly revised one
        if sharedata.vposvalid and privatedata.symbolattrs is not None:
            x_pt, y_pt = graph.vpos_pt(*sharedata.vpos)
            if self.setsize<0:
                siz=privatedata.size_pt*point[self.sizecolumnname]
            else :
                siz=privatedata.size_pt*self.setsize
            if     self.setcolor:
                color= self.setcolor
            else:
                color = self.gradient.getcolor(point[self.colorcolumnname])
            col =privatedata.symbolattrs + [color]
            privatedata.symbol(privatedata.symbolcanvas, x_pt, y_pt, siz, col)

def apply_on_not_none(*args,function=None):
    nn=not_none(*args)
    if len(nn):
        return function(nn)
    else:
        return None

def not_none(*args):
    return [arg for arg in args if arg is not None]

if __name__ == "__main__":
    nargs=len(sys.argv);
    args=sys.argv[1:];

    seplot=Splotter(arguments=args)
    seplot.make_and_save()
