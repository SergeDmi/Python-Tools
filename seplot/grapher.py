from numpy import *
import sys
import sio_tools as sio
import pandas as pd


from seplot.styler import Style
import seplot.kw_dictionaries as kd
import seplot.style_dictionaries as sd


"""
Grapher is a sub-module defining the class Graph.
"""


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


class Graph:
    """
    Graph is a class containing a single line/set of points and their style, created from class Toplot.
    """
    def __init__(self,*args,
                x=0,y=1,dx=[],dy=[],col='',siz='',stil='',labels=[],
                cond=[],range=[],
                function_string='',legend='',
                fname='',data=None,numr=0,mode='v',
                n_points='200',
                **kwargs):
        """ Instance initialization """


        self.fname=fname ; self.function_string=function_string
        #self.data=array(data)
        #self.data=array([])
        self.numr=numr
        self.mode=mode ; self.numr=numr
        self.dX=[] ; self.dY=[]
        self.X=[] ; self.Y=[] ; self.S=[] ; self.C=[]
        self.is_function=0
        self.is_histogram=0
        self.make_histogram=0
        self.xlabel=None ; self.ylabel=None

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
        else:
            if data is not None:

                if isinstance(data, list):
                    data = ndarray(data)
                if isinstance(data, ndarray):

                    s = data.shape

                    if len(s)<2:
                        data = ndarray([data])
                        s = data.shape

                    if not len(labels):
                        labels = [None]*s[1]
                    in_data = { "data" : data, "size_x" : s[0] , "size_y" : s[1] , "labels": labels }

                if isinstance(data, pd.DataFrame):
                    in_data = sio.import_array_from_frames(data)

            else:
                in_data=sio.data_import_wrapper(self.fname)

            try:
                A=in_data['data']
                self.data=A
            except:
                raise ValueError("Error : no suitable data, nor function given")

            # Dirty tricks for maximum compatibility
            if min(in_data['size_x'],in_data['size_y'])==1:
                x='auto'
                y=0
                sio.custom_warn("Single data row/column : x is automatic")
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


            for i,label in enumerate(self.labels):
                self.label_dict[label]=i

        # Are we plotting a histogram ?
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
                    if not var(self.C)<sys.float_info.epsilon:
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
        """ A function to automatically make a legend """
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
        """ Initial values of X and Y, usefull to later apply conditions """
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

    def set_label(self,label,coord):
        """ sets a label for coordinate x or y """
        if coord=='x':
            self.xlabel=label
        elif coord=='y':
            self.ylabel=label
        return

    def set_from_input(self,A,input,coord):
        """ Tries to compute a variable of name coord from an input, usually a string or number, using the data A"""
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
        """ Substitutes names by values"""
        i=self.label_dict[label]
        if self.mode=='h':
            replace='A[%s,:]' %i
        else:
            replace='A[:,%s]' %i
        return input.replace(label,replace)

    def set_A_range(self,A,in_range):
        """ Selects only a range of data """
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
        """ Selects data by condition """
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



def get_histogram(Y,bins='auto'):
    """ A wrapper for numpy's histogram """
    (Y,X)=histogram(Y,bins)
    nx=len(X)
    if nx:
        X=(X[0:(nx-1)]+X[1:nx])/2.0
    else:
        raise ValueError('Empty histogram from numpy.histogram')
    return (Y,X)