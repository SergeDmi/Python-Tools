# Installation

 ## Install from pip
 ```shell
 $ pip install splot
```

## Install from github

# Usage

## Basic usage
Splot is meant to be used from command line or from a python script. The typical command line instruction to plot from a file data.txt would be :
```shell
	$ splot.py data.txt
```
By omitting further instructions, it is implied that the data in $data.txt$ is a set of vertical columns, and we plot column $1$ as a function of column $0$. Here we will use Python's zero-indexing convention (column $0$ is the first column). This could also be written :
```shell
	$ splot.py data.txt mode=v x=0 y=1 out=plot.pdf
```

Where mode  is v (vertical) for columns of data and v for rows (horizontal), and plot.pdf is the outputfile. Of course several files can be plotted with different colors :
```shell
	$ splot.py data_1.txt color=red data_2.txt color=blue
```
We can also plot several columns from the same file, use columns for errorbars dx and dy, and plot a function :
```shell
	$ splot.py data_1.txt x=0 dx=1 y=2 dy=3 color=4 size=5
		   function='y(x)=x'
```
Here, we even used data to assign a size and color to the plot symbols ! Note that Splot can easily be used from inside a python script :
```python
import splot
# A is an array containing the data
plot=splot.Splotter(data=A)
plot.make_and_save()
```
In the rest, I will use only the command-line calls to splot, but they can equally easily be accessed through python scripts.

For now  I illustrated the simplicity of Splot. What about its capabilities ?

### Data manipulation and conditional expressions
It is frequent that we want to plot not directly the points saved in a file, but a function of them. A challenge is to offer this possibility to the user with a simple syntax, and without arbitrarily limiting the available function space. This is done using Python's *eval()* function. Data read from the data file (eg. data.txt) is stored in a numpy array called *A*. We can apply any numpy function on *A* in *Splot* through a simple syntax :
```shell
	$ splot.py data.txt y='A[:,1]^2'
```
Here *A[:,1]* is the *second* column of *A*. We can use the same syntax for conditional expressions using the keyword **if** :
```shell
	$ splot.py data.txt y='A[:,1]^2' if='A[:,1]>0'
```
We can now combine several features :
```shell
	$ splot.py data.txt y='A[:,1]^2' if='A[:,1]>0' color=blue
		   and if='A[:,1]<0' color=red
```
Here, we used the **and** keyword to re-use the data from *data.txt* into another plot element (note that the shorthand  {\color{deepblue}andif=}... is also supported).

This is, in my regard, the most powerful and interesting feature of Splot, allowing to easily compute and plot complex functions of the input data :
```shell
	$ splot.py data.txt y='sqrt(1/(1+A[:,1]^2))/A[:,2]
				+sin(A[:,3])'
```
Additionally, we can conveniently select a sub-set of the data, both by *first* choosing a range of lines (resp. columns in horizontal mode), and *second* a conditional expression, e.g. :
```shell
	$ splot.py data.txt range='0:10' if='A[:,1]>0'
```
Here data from the first 10 lines (lines 0-9 according to Python's numbering convention) if the value of the second columns (*A[:,1]*) is larger than 0.

### Styles and propagation
Splot allows for a wide variety of symbol and line styles and attributes. Some have shorthands, but any style from PyX can be used. For instance let us plot the same data as red dots, a blue solid line, and a thick black dashed line.
```shell
	$ splot.py data.txt color=red style=o and color=blue style=_
		  and color=black style=-- line=4
```
Other symbols include "+" (vertical cross), "x" (cross), ">" or "<" (triangle), but any of PyX's  **graph.style.symbol** can be used.

When using color-by-value, any of PyX's gradients can be used, and some have shorthands :
```shell
	$ splot.py data.txt color=2 gradient=jet and gradient=gray
```

To keep the same style between two files, and change style for another file, we can use the **-keep** and **-discard** keywords :
```shell
	$ splot.py data_0.txt color=red -keep 'data_1.txt'
		   -discard 'data_2.txt'
```
Note than **-keep** and **-discard** keep or discard any option, including **y=**, **range=**, **if=** , etc.

### Labels and titles
One of the main interest on using PyX as a backend is to have full *LaTeX* compatibility. Therefore we can happily write :
```shell
	$ splot.py data.txt xlabel='time ($s$)'
			  ylabel='$v$ ($m s^{-1}$)'
```
Splot also can read directly the label from a text file using the keyword  **-autolabel**. For example for a file with a simple header  &#35; time position}:
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
	$ splot.py data.txt -autolabel
```
Which will yield *xlabel}=time* and  *ylabel=position*.

We can also specify the position of the graph legend, e.g. with *key=tl* for the top left :
```shell
	$ splot.py data.txt -autolabel key=tl
```
## Calling splot from Python}
I already mentioned that we could call splot from a Python script. This offers many possibility, including appending progressively plots during analysis, etc. This can be achieved easily :
```python
import splot
plot=splot.Splotter(key='tl')
for i,A in enumerate(list_of_data):
		# A is an element of list_of_data
		# i is its index
		plot.add_plot(data=A,title=i)
plot.make_and_save()
```
