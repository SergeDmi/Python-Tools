from setuptools import setup, Extension, find_packages
import re

def find_version(fname):
    with open(fname,'r') as file:
        version_file=file.read()
        version_match = re.search(r"__VERSION__ = ['\"]([^'\"]*)['\"]",version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

with open("seplot/README.md", "r") as handle:
    splot_description = handle.read()

version=find_version("seplot/seplot.py")

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
      'sio_tools',
      'pandas'
    ],
    packages=['seplot'],
    package_dir={'seplot': 'seplot'},
    scripts=['seplot/bin/seplot','seplot/seploter.py'],
    package_data={'seplot': ['README.md']}
 )
