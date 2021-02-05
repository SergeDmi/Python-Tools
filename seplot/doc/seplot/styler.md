Module seplot.styler
====================
A sub-module to deal with plot styles

Classes
-------

`Goodstyle(*args, numr=0, col='', siz='', line='', stil='', gradient='', is_function=0, color_from_data=False, **kwargs)`
:   A class containing the style attributes to pass to python PyX

    ### Instance variables

    `gradient`
    :   gradient colors

    `kind`
    :   kind of plot : symbol, line, etc.

    `linest`
    :   linestyle

    `linew`
    :   linewidth

    `setcolor`
    :   color set to be plotted

    `setsize`
    :   size of the symbol

    `stroke_style`
    :   stroke style

    `symbol`
    :   what kind of symbol to plot

`Style(*args, numr=0, dx=None, dy=None, **kwargs)`
:   A class containing the style to make a graph
    
    Input :
    -*args
    -numr : a plot number for automatic style selection
    -

    ### Instance variables

    `dxy`
    :   Style for error barys

    `goodstyle`
    :   Style attributes

    `stroke_style`
    :   Actual stroke style

    `style`
    :   A style array

`changesymbol(sizecolumnname='size', colorcolumnname='color', gradient=<pyx.color.functiongradient_hsb object>, symbol=<pyx.attr.changelist object>, symbolattrs=[<pyx.deco._filled object>, <pyx.deco._stroked object>], setsize=0.5, kind='symbol', linew=False, linest=False, setcolor=<pyx.color.gray object>, numr=0, stroke_style=None, **kwargs)`
:   A flexible symbol class derived from PyX's very own changesymbol class

    ### Ancestors (in MRO)

    * pyx.graph.style.symbol
    * pyx.graph.style._styleneedingpointpos
    * pyx.graph.style._style

    ### Methods

    `columnnames(self, privatedata, sharedata, agraph, columnnames, dataaxisnames)`
    :   register the new column names

    `drawpoint(self, privatedata, sharedata, graph, point)`
    :   replace the original drawpoint method by a slightly revised one