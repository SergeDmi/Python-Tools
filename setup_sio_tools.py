from setuptools import setup
from sio_tools import sio_tools as sio

version=sio.__VERSION__
print(version)

setup(
     name='sio_tools',
     version=version,

     author="Serge Dmitrieff",
     description="I/O tools for seplot and other python projects",
     url="https://github.com/SergeDmi/Python-Tools/",
     install_requires=[
          'numpy'
      ],
     packages=['sio_tools' ]
 )
