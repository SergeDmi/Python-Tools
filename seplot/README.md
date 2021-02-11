# About seplot
seplot is a frontend for PyX to create plot from text files in command line or through a python interface.
Developed by Serge Dmitrieff.
https://www.biophysics.fr

# Installation

## Installing with pip3 (recommended)
```shell
 $ pip3 install seplot
```

## Required packages
seplot requires PyX, Numpy, pandas, and sio_tools. They will be downloaded when installed with pip3.

# Usage

## Basic usage
seplot is meant to be used from command line or from a python script. The typical command line instruction to plot from a file data.txt would be :
```shell
$ seplot data.txt
```
By omitting further instructions, it is implied that the data in data.txt is a set of vertical columns, and we plot column 1 as a function of column 0. seplot uses Python's zero-indexing convention (column 0 is the first column). This could also be written :
```shell
$ seplot data.txt mode=v x=__0__ y=__1__ out=plot.pdf
```
Where **mode**  is **v** (vertical) for columns of data and **h** for rows (horizontal), and plot.pdf is the output file.  

When using a *.csv* file, or a *.txt* file with a header, we can use directly the column names :
```shell
$ seplot data.txt x=time y=distance
```
Where *data.txt* looks like :
```
# time distance 
0 1.0
1 2.0
...
```
 For a csv file :  
```shell
$ seplot data.csv x=time y=distance
```
Where *data.csv* looks like :
```
,time,distance
,0,1.0
,1,2.0
...
```
 
 Of course several files can be plotted with different colors :
```shell
$ seplot data_1.txt color=red data_2.txt color=blue
```
We can also plot several columns from the same file, use columns for errorbars dx and dy, and plot a function :
```shell
$ seplot data_1.txt x=__0__ dx=__1__ y=__2__ dy=__3__ color=__4__ size=__5__ function='y(x)=x'
```
Here, we even used data to assign a size and color to the plot symbols ! Note that seplot can easily be used from inside a python script :
```python
import seplot.seplot as sp
plot=sp.Splotter(file='data.txt')
# alternatively, with A an array containing the data
plot.add_plot(data=A)
plot.make_and_save()
```
This readme focuses on the command-line interface, but all instructions can also be used equally easily through the python interface.

### Ploting with several styles
```shell
$ seplot data.txt x=__0__ y=__1__ dy=__2__ and x=__0__ y=__1__ line=1
```
Does a scatter plot of the second column as a function of the first, using the third column for error bars. Then does a line plot of the secund column as a function of the first.

### Histograms
```shell
$ seplot data.txt y=__0__ -hist
```
Does a histogram of values of the first column (y=0) of data.txt

```shell
$ seplot data.txt -hist x=10 y=__0__ style=b data.txt -hist x='[0,1,2,3,4]' style=B
```
Does a histogram of the first column (y= __0 __) of data.txt, with 10 bins (x=10) and then with bins centered around 0,1,2,3,4 (and filled bars : style=B)

### Data manipulation and conditional expressions
 We can perform operations on the input data. For a csv file, or a text file with header, we can use directly the column names as if it was the values :
```shell
$ seplot data.csv y='distance*distance'
```
Any python/numpy operation on the data is permitted. If the data is not directly named (text file without header), it is still possible to perform operation on the data.  
Data read from the data file (eg. data.txt) is stored in a numpy array called *A*. We can apply any numpy function on *A* in *seplot* through a simple syntax :
```shell
$ seplot data.txt y='A[:,1]^2'
```
Here *A[:,1]* is the *second* column of *A*.  

We can use the same syntax for conditional expressions using the keyword **if** :
```shell
$ seplot data.txt y='distance*distance' if='y>1'
```
We can now combine several features :
```shell
$ seplot data.txt y='distance*distance' if='y>1' color=blue
		   and color=red if='y<1'
```
We used the **and** keyword to re-use the data from *data.txt* into another plot element (note that the shorthand  **andif=**... is also supported).

We can easily compute and plot complex functions of the input data :
```shell
$ seplot data.txt y='sqrt(distance*distance)/time' color='sin(time)'
```
Similarly, the **if** keyword can be used for any function of the input data :
```shell
$ seplot data.txt y='A[:,1]^2' if='sqrt(A[:,1])>10'
```
Additionally, one can  select a sub-set of the data, both by *first* choosing a range of lines (resp. columns in horizontal mode), and *second* a conditional expression, e.g. :
```shell
$ seplot data.txt range='0:10' if='A[:,1]>0'
```
Here data from the first 10 lines (lines 0-9 according to Python's numbering convention) if the value of the second columns (*A[:,1]*) is larger than 0.

### Styles and propagation
seplot allows for a wide variety of symbol and line styles and attributes. Some have shorthands, but any style from PyX can be used. For instance let us plot the same data as red dots, a blue solid line, and a thick black dashed line.
```shell
$ seplot data.txt color=red style=o and color=blue style=_ and color=black style=-- line=4
```
Other symbols include "+" (vertical cross), "x" (cross), ">" or "<" (triangle), but any of PyX's  **graph.style.symbol** can be used.

When using color-by-value, any of PyX's gradients can be used, and some have shorthands :
```shell
$ seplot data.txt color=__2__ gradient=jet and gradient=gray
```

To keep the same style between two files, and change style for another file, we can use the **-keep** and **-discard** keywords :
```shell
$ seplot data_0.txt color=red -keep 'data_1.txt' -discard 'data_2.txt'
```
Note than **-keep** and **-discard** keep or discard any option, including **y=**, **range=**, **if=** , etc.

### Labels and titles
One of the main interest on using PyX as a backend is to have full *LaTeX* compatibility. Therefore we can happily write :
```shell
$ seplot data.txt xlabel='time ($s$)' ylabel='$v$ ($m s^{-1}$)'
```
seplot also can read directly the label from a text file using the keyword  **-autolabel**. For example for a file with a simple header  &#35; time position}:
```shell
$ cat data.txt
	# time position
	0 1
	1 2
	2 3
	3 4
```
We can use the instruction :
```shell
$ seplot data.txt -autolabel
```
Which will yield *xlabel=time* and  *ylabel=position*.

We can also specify the position of the graph legend, e.g. with *key=tl* for the top left :
```shell
$ seplot data.txt -autolabel key=tl
```
## Calling seplot from Python
Calling seplot from a Python script offers many possibility, including appending progressively plots during analysis, etc.
```python
import seplot.seplot as sp
plot=sp.Splotter(key='tl')
for i,A in enumerate(list_of_data):
		# A is an element of list_of_data
		# i is its index
		plot.add_plot(data=A,title=i)
plot.make_and_save()
```

Global options are passed when calling **seplot.Splotter** and local options are passed when calling **plot.add_plot**, following the same syntax as the command line. One exception, **if=** (from command line) becomes **cond=** to avoid confusion.
```python
import seplot.seplot as sp
plot=sp.Splotter(key='tl')
plot.add_plot(file='data.txt',cond='A[:,0]>0')
plot.make_and_save()
```

## Detailed option list
### Global options
**xlabel=**        : label of x axis  
**ylabel=**        : label of y axis  
**width=**         : width of figure  
**height=**        : height of figure  
**xmin=**          : min x value  
**xmax=**          : max x value  
**ymin=**          : min y value  
**ymax=**          : max y value  
**key=**           : position of figure legend (tr,br,tl,bl)  
**out=**           : name of output file  
**-ylog**         : y axis is logarithmic  
**-xlog**         : x axis is logarithmic  
**-keep**         : keep options for subsequent plots, until -discard  
**-discard**      : discard options for next plot  
**-equal**        : equal x-y axis range  
**-autolabels**   : tries to automatically find labels from data file  

### Local options (per plot)
**x=**        : index of column or row to be used as x axis values (e.g. x=0 for the first column)  
                also can specify an operation : x='A[:,0]*A[:,1]'  
                also can specify a label read from file header : x=first_column_label  
                can also be automatic, i.e. index : x=auto  
**y=**        : index of column or row to be used as y axis values (e.g. x=0 for the first column)  
                also can specify an operation : y='A[:,1]*A[:,2]/A[:,3]'  
**dy=**       : index of column or row to be used as dy values (e.g. x=0 for the first column)  
                also can specify an operation : dy='A[:,2]/sqrt(A[:,3])'  
**mode=**     : h for horizontal (rows), v for vertical (column) (default)  when reading data  
**color=**    : color of lines or symbol ; can be either red, green, blue, dark, medium, light, black  
                or color.cmyk.*  or color.rgb.*,
                or an operation, e.g. color=A[:,2]  
**and=**      : add another graph (possibly with different options)  
**style=**    : style of plot : - or _ for a line, -- for dashed, .- for dashdotted  
                            o for circles  x , * for crosses  + for plus   > , <     for triangles
                            b for a bar graph, B for a filled bar graph  
**if= / cond=** : condition to keep the rows or columns    
**andif=**     :  add another graph with different conditions    
**range=**    : range of rows / columns to plot  
**size=**     : size of symbol used  
**line=**     : thickness of line, from 0 to 5  
**title= / legend=** : title of the graph  
**-hist**     : makes a histogram  