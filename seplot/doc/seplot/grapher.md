Module seplot.grapher
=====================

Functions
---------

    
`get_histogram(Y, bins='auto')`
:   A wrapper for numpy's histogram

Classes
-------

`Graph(*args, x=0, y=1, dx=[], dy=[], col='', siz='', stil='', labels=[], cond=[], range=[], function_string='', legend='', fname='', data=None, numr=0, mode='v', n_points='200', **kwargs)`
:   Graph is a class containing a single line/set of points and their style, created from class Toplot.
    
    Instance initialization

    ### Methods

    `make_auto_legend(self, legend)`
    :   A function to automatically make a legend

    `set_A_condition(self, A, cond)`
    :   Selects data by condition

    `set_A_range(self, A, in_range)`
    :   Selects only a range of data

    `set_from_input(self, A, input, coord)`
    :   Tries to compute a variable of name coord from an input, usually a string or number, using the data A

    `set_init_XY(self, A)`
    :   Initial values of X and Y, usefull to later apply conditions

    `set_label(self, label, coord)`
    :   sets a label for coordinate x or y

    `set_n_points(self, arg)`
    :

    `substitute_label(self, input, A, label)`
    :   Substitutes names by values