from setuptools import setup
from seplot import seplot as sep

with open("seplot/README.md", "r") as handle:
    splot_description = handle.read()

version=sep.__VERSION__

setup(
     name='seplot',
     version=version,



     author="Serge Dmitrieff",
     description="A front-end for Python PyX",
     long_description=splot_description,
     url="https://github.com/SergeDmi/Python-Tools/",
     install_requires=[
          'pyx',
          'numpy',
          'sio_tools'
      ],
     packages=['seplot' ],
     scripts=['seplot/bin/seplot','seplot/seplot.py' ]
 )
