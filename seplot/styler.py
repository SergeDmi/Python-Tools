from numpy import *
from pyx import *
import sio_tools as sio


import seplot.kw_dictionaries as kd
import seplot.style_dictionaries as sd


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


"""
A sub-module to deal with plot styles
"""



class Style:
    """
      A class containing the style to make a graph

    Input :
    -*args
    -numr : a plot number for automatic style selection
    -
    """
    def __init__(self, *args,numr=0,
                dx=None,dy=None,
                **kwargs):

        self.style=[]
        """ A style array """
        self.dxy=[]
        """ Style for error barys"""
        self.stroke_style=[]
        """ Actual stroke style """
        if numr:
            kwargs['numr']=numr
        self.goodstyle=Goodstyle(*args,**kwargs)
        """ Style attributes """

        if self.goodstyle.kind=='histogram':
            self.is_histogram=1

        if dx is not None or dy is not None:
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


class Goodstyle:
    """
    A class containing the style attributes to pass to python PyX
    """
    def __init__(self,*args,
                numr=0,
                col='',siz='',line='',stil='',gradient='',
                is_function=0,color_from_data=False,
                **kwargs):

        self.kind='symbol'
        """ kind of plot : symbol, line, etc."""
        self.setcolor=colours[int(ceil(numr/4)) %4]
        """ color set to be plotted"""
        self.symbol=symbols[numr %4]
        """ what kind of symbol to plot"""
        self.setsize=0.5
        """ size of the symbol"""
        self.linew=style.linewidth.thin
        """ linewidth"""
        self.linest=linests[numr %4]
        """ linestyle """
        self.gradient=color.gradient.Rainbow;
        """ gradient colors"""
        self.stroke_style=[]
        """ stroke style"""

        # By default, function should be a line
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
                if not gradient.startswith('color.gradient'):
                    # shorthand notation is tolerated
                    if gradient.startswith('gradient'):
                        gradient='color.%s' %(gradient)
                    else:
                        gradient='color.gradient.%s' %(gradient)
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
    """
     A flexible symbol class derived from PyX's very own changesymbol class
     """
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
        """ register the new column names"""
        if self.sizecolumnname not in columnnames:
            raise ValueError("column '%s' missing" % self.sizecolumnname)
        if self.colorcolumnname not in columnnames:
            raise ValueError("column '%s' missing" % self.colorcolumnname)
        return ([self.sizecolumnname, self.colorcolumnname] +
                graph.style.symbol.columnnames(self, privatedata, sharedata, agraph,
                                               columnnames, dataaxisnames))

    def drawpoint(self, privatedata, sharedata, graph, point):
        """ replace the original drawpoint method by a slightly revised one"""
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