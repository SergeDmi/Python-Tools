## About seplot
seplot is a frontend for PyX to create plot from text files in command line or through a python interface.
Developed by Serge Dmitrieff.
https://www.biophysics.fr

## Installation

### Installing with pip3 (recommended)
 ```shell
 $ pip3 install ply_convert
```

### Required packages
ply_convert requires Sklearn, Numpy, plyfile, and sio_tools. They will be downloaded when installed with pip3.


## Syntax 
```shell
   ply_convert [INPUT_FILE [INPUT_FILE_2 _3 ... ]] [out=OUTPUT_FILE] [OPTION=VALUE]  [-ADDITIONAL_OPTIONS]
```


### OPTIONS

    Options are to be written as opt=value or -option  
    Unless mentioned otherwise, options are not applied by default  

    Supported options :  
        out=            : name of output file (single file job) // extension of output file (multiple files)  
        scale=          : scale to be applied to points (float or 3x1 vector)  
        length=         : length of object on dimension of maximal variance  
        thickness=      : adds to each point a vector thickness*normal  
        batch=          : apply to all files of a certain type  
        path=           : path in which to look for files for batch operation  
        label=          : label of mesh, added when saving mesh files  
        orientation=    : orientation of normals (+1 : towards outside, -1 : towards inside)  
        prefix=         : add a prefix to output file name (multiple files)  
        suffix=         : add a suffix to output file name (multiple files)  
        -center         : center the data around [0,0,0]  
        -align          : aligns data to dimension x  
        -normals        : computes normals from faces  
        -verbose        : verbose output  
        -fixnorms       : makes sure normals are inwards (equivalent to option orientation=-1)  
        -fixuint        : fixes format to meshlab-friendly  

        batch=          : extension of files to process in batch (support multiple)  
        ** batch only **  
        path=            : folder in which to look for files (support multiple)  
        include=         : string that *must* be included in file name (support multiple)  
        exclude=         : string that *must not* be included in file name (support multiple)  
        -recursive       : searches recursively for files  

### EXAMPLES :
```shell
            ply_convert file.ply out=file.mesh  
```
converts a ply file file.ply to a mesh file file.mesh  

```shell
            ply_convert.py file.mesh normals=1 out=file.ply  
```
converts a mesh file to a ply file, and computes the normal at each point  

```shell
            ply_convert file_1.ply file_2.ply file_3.ply out=.mesh  
```
converts file_1.ply file_2.ply file_3.ply into mesh files  

```shell
            ply_convert file.ply -center -align -normals length=7 -verbose thickness=0.15 scale='1.0 1.0 2.0'
                                verbose=1 out=thickened.mesh out=thickened.ply  
```
converts a ply file to a ply and a mesh file after centering, aligning, computing normals, scaling the object to a length of 7, and adding an extra thickness of 0.15, then scaling the z axis with a factor 2  

```shell
            ply_convert.py batch=.ply path='/home/user/simulations/' out='.ply' scale=0.1 -recursive prefix=scaled_   
```
Recursively find ply files in '/home/user/simulations/', scales them to a factor of 0.1, and                         saves them to FOLDER/suffix_NAME.ply with NAME the filename and FOLDER the folder name
```shell
            ply_convert.py file.ply out=fixed_file.ply -fixuint  
```
fixes the header of a mesh file saved by tinyply (C++) so that it doesn't crash with meshlab.


