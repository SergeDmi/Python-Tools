from setuptools import setup, Extension
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
     long_description_content_type='text/markdown',
     url="https://github.com/SergeDmi/Python-Tools/",
     install_requires=[
          'pyx',
          'numpy',
          'sio_tools'
      ],
     packages=['seplot' ],
     scripts=['seplot/bin/seplot','seplot/seplot.py' ]
 )
