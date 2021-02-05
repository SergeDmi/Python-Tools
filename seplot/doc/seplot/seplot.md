Module seplot.seplot
====================

Functions
---------

    
`apply_on_not_none(*args, function=None)`
:   

    
`not_none(*args)`
:   

    
`version()`
:   

Classes
-------

`Splotter(*args, arguments=None, data=None, **kwargs)`
:   Splotter is the global plotter class
    It mostly sorts arguments and prepares global plot options
    
    Arguments passed :
    - arguments=: a list of arguments and kw arguments (those include "=")
    - data= : an array/dataframe containing data to be plotted
    - *args : additional arguments
    - **kwargs : additional keyword arguments
    
    Initiation  from arguments and keyword arguments

    ### Instance variables

    `autolabel`
    :   if we auto label axes

    `bgcolor`
    :   background color

    `canvas`
    :   The canvas (see PyX)

    `equalaxis`
    :   if axes are equal

    `future_plots`
    :   the list items to be plotted,

    `graph`
    :   The graph itself, an instance of PyX.graph.graphxy

    `graphs`
    :   the list of created graphs

    `height`
    :   graph height

    `kdist`
    :   distance of the legend

    `key`
    :   position of the legend (string, cf PyX)

    `out`
    :   The name of the output file

    `width`
    :   graph width

    `xlabel`
    :   xlabel

    `xlog`
    :   if x axis in log scale

    `xmax`
    :   mas value of x axis

    `xmin`
    :   min value of x axis

    `ylabel`
    :   ylabel

    `ylog`
    :   if y axis in log scale

    `ymax`
    :   max value of y axis

    `ymin`
    :   min value of y axis

    ### Methods

    `add_plot(self, *args, **kwargs)`
    :   a wrapper to add a plot to future_plots

    `get_data_extrema(self)`
    :

    `make_and_save(self, *args, **kwargs)`
    :

    `make_equal_axis_range(self)`
    :

    `make_plot(self, *args, **kwargs)`
    :   We do the plotting by dispatching the arguments to PyX. Arguments can be passed again !

    `plot(self, graf)`
    :   A wrapper for PyX.graph.plot

    `read_args(self, *args, arguments=None, **kwargs)`
    :   Where actually we read arguments !
        inputs :
        - arguments= : a list of arguments or kwarguments
        - *args : additional arguments
        - *kwargs : additional keyword arguments

    `save_plot(self, *args, out=None, **kwargs)`
    :   Saving canvas to a file

    `usage(self)`
    :

`Toplot(*args, arguments=None, data=None, fname='', **kwargs)`
:   Toplot is a class containing the options for plotting
    it also contains a method to split into two
    here we need to support a keyword argument having to values, until we split
    therefore we don't convert everything to *args and **kwargs,
    rather we pass *argument*, a list of arguments and kw arguments
    
    Initialization

    ### Instance variables

    `arguments`
    :   actual arguments

    `data`
    :   data to plot from

    `fname`
    :   filename to read data from

    ### Methods

    `check_split(self)`
    :   Checking if we need to split the graph into several graphs when implied from arguments

    `unpack_arguments(self)`
    :   We convert our coarse list of arguments as a list of strings to a better arg / kwargs format