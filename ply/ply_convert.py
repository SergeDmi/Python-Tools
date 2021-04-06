#!/home/dmitrief/conda3/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright Serge Dmitrieff
# www.biophysics.fr

# @TODO : clear input. Maybe get rid of batch !
# @TODO : different scales on different directions
# @TODO : support for complex mesh (non triangular)
# @TODO : Document and clarify submesh

__VERSION__ = "0.0.4"

"""
# SYNOPSIS

    ply_convert is a command line tool to convert and perform simple tasks on .mesh and .ply files

# DESCRIPTION

    ply_convert reads a mesh from a file (.mesh or .ply), performs simple operations, and saves it (to .mesh or .ply)
    Requires module plyfile : https://github.com/dranjan/python-plyfile/
    Requires modules sys,os,numpy,sklearn
    Uses the module sio_tools : $ pip3 install sio_tools
    https://github.com/SergeDmi/Python-Tools/blob/master/sio_tools/sio_tools.py
    More : https://biophysics.fr

# SYNTAX

   python ply_convert.py [INPUT_FILE [INPUT_FILE_2 _3 ... ]] [out=OUTPUT_FILE] [OPTION=VALUE]  [-ADDITIONAL_OPTIONS]

# OPTIONS

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

# EXAMPLES :

            ply_convert.py file.ply out=file.mesh
                        converts a ply file file.ply to a mesh file file.mesh


            ply_convert.py file.mesh normals=1 out=file.ply
                        converts a mesh file to a ply file, and computes the normal at each point

            ply_convert.py file_1.ply file_2.ply file_3.ply out=.mesh
                        converts file_1.ply file_2.ply file_3.ply into mesh files


            ply_convert.py file.ply -center -align -normals length=7 -verbose thickness=0.15 scale='1.0 1.0 2.0'
                                verbose=1 out=thickened.mesh out=thickened.ply
                        converts a ply file to a ply and a mesh file
                        after centering, aligning, computing normals, scaling the object to a length of 7,
                        and adding an extra thickness of 0.15, then scaling the z axis with a factor 2


            ply_convert.py batch=.ply path=FOLDER out='.ply' scale=0.1 -recursive prefix=PREFIX_
                        Recursively find ply files in '/home/user/simulations/', scales them to a factor of 0.1, and
                        saves them to FOLDER/PREFIX_NAME.ply with NAME the filename and FOLDER the folder name


            ply_convert.py file.ply out=fixed_file.ply -fixuint
                        fixes the header of a mesh file saved by tinyply (C++) so that it doesn't crash with meshlab.


"""
# ------------------------------------------------------------------------
## Python modules                                                   ------
# ------------------------------------------------------------------------
try:
    from numpy import *
    from plyfile import PlyData, PlyElement
    import sys
    from os import listdir,path
    from sklearn.decomposition import PCA
    from collections.abc import Iterable
    import sio_tools as sio
except:
    raise ValueError('Necessary Python modules could not be loaded')

## Version
def version():
    return __VERSION__

# ------------------------------------------------------------------------
## ---- DAT MESH CLASS  doin work                                   ------
# ------------------------------------------------------------------------
class Mesh:
    """
    Mesh class containing arguments and mesh elements
    Creates a mesh from a file name and list of argument
    Contains methods to manipulate the mesh
    Contain a method to read arguments and do the required operatipns
    """
    # Mesh elements are of the class PlyElement from module plyfile
    # We could also directly have the data in Plydata
    # but it does appear more flexible this way

    # creator loads files but does not populate elements
    # This is done in self.initialize()
    def __init__(self,fname_in,args):
        """
        Creates the MESH

        Parameters
        ----------
        arg1 : str
            file name to load from
        arg2 : list
            list of arguments
        """

        plydata=load_from_file(fname_in,args)
        self.arguments=[arg for arg in args]
        self.in_elements=[elem for elem in plydata.elements]
        self.elements=[]

    # Populates self.elements from self.in_elements
    def initialize(self):
        self.verify_elements()

    # write the elements to a ply or mesh file
    def write_to_file(self):
        plydata=PlyData(self.elements)
        return write_ply_to_file(plydata,self.arguments)

    # We can get an element by its name (e.g. 'vertex' 'face')
    def get_element_by_name(self,name):
        for ix,elem in enumerate(self.elements):
            if elem.name==name:
                return ix,elem

    def get_in_element_by_name(self,name):
        for ix,elem in enumerate(self.in_elements):
            if elem.name==name:
                return ix,elem
    # We need the ply files to have some simularity :
    #   normals should be at least existent, if not computed
    #   faces should be called vertex_index, not vertex_indices
    def verify_elements(self):
        count=-1
        args=self.arguments
        ixmin=0
        filter=0
        faces_only=0
        for arg in args:
            if arg.startswith('-faces_only'):
                faces_only=1
                filter=1
                (ix_v,vertices)=self.get_in_element_by_name('vertex')
                (ix_f,faces) =self.get_in_element_by_name('face')
                # list of vertices in the faces !
                ixes=sort(unique(array([face[0] for face in faces])))
                n_verts=len(ixes)
                new_ixes=arange(n_verts)
                convert=-ones((max(ixes)+1,))
                convert[ixes]=new_ixes


        for elem in self.in_elements:
            count+=1
            # First if we deal with faces, we make sure the name is correct
            if elem.name=='face':
                # we convert vertex_indices into vertex_index
                for prop in elem.properties:
                    if prop.name.startswith('vertex_'):
                        if faces_only:
                            face=array([([convert[T[0][0]],convert[T[0][1]],convert[T[0][2]]],) for T in elem],dtype=[('vertex_index','i4',(3,))])
                        else:
                            face=array([([T[0][0],T[0][1],T[0][2]],) for T in elem],dtype=[('vertex_index','i4',(3,))])
                        elem=PlyElement.describe(face,elem.name)
            elif elem.name=='vertex':
                # we check if normals are defined, otherwise we have to create them
                if not '-normals' in self.arguments:
                    self.arguments.append('-normals')
                if len(elem[0])<6:
                    if filter==0:
                        face=array([(l[0],l[1],l[2],0.0,0.0,0.0) for l in elem],dtype=[('x','f4'),('y','f4'),('z','f4'),('nx','f4'),('ny','f4'),('nz','f4')])
                    else:
                        face=array([(l[0],l[1],l[2],0.0,0.0,0.0) for j,l in enumerate(elem) if j in ixes],dtype=[('x','f4'),('y','f4'),('z','f4'),('nx','f4'),('ny','f4'),('nz','f4')])
                    elem=PlyElement.describe(face,elem.name)
                elif filter:
                    face=array([(l[0],l[1],l[2],l[3],l[4],l[5]) for j,l in enumerate(elem) if j in ixes],dtype=[('x','f4'),('y','f4'),('z','f4'),('nx','f4'),('ny','f4'),('nz','f4')])
                    elem=PlyElement.describe(face,elem.name)
            self.elements.append(elem)

    # Here we read arguments and do what we gotta do
    def do_mesh_processing(self):
        # see function declaration for what arguments do
        for arg in self.arguments:

            if arg.startswith("scale="):
                try:
                    scale=float(arg[6:])
                    self.scale_mesh(scale)
                except:
                    try:
                        scale=nums(arg[6:])
                        self.scale_mesh(scale)
                    except:
                        raise ValueError('Could not read from argument scale')

            if arg.startswith("-center"):
                self.center_mesh()

            #if arg.startswith("-faces_only"):
            #    self.keep_only_faces()

            if arg.startswith("length="):
                length=float(arg[7:])
                self.set_mesh_length(length)

            if arg.startswith("-align"):
                self.align_mesh()

            if arg.startswith("-normal"):
                self.recompute_normals()

            if arg.startswith("-fixnorm"):
                self.fix_face_normals()

            if arg.startswith("orientation="):
                orientation=arg[12:]
                self.fix_face_normals(orientation)

            if arg.startswith("thickness="):
                thickness=float(arg[10:])
                self.add_thickness(thickness)

            if arg.startswith("-verbose"):
                print_ply_info(plydata)

            if arg.startswith("-fixuint"):
                self.change_face_dtype_to_int()

        return

    # We center the mesh around 0
    def center_mesh(self):
        elem=self.get_element_by_name('vertex')[1]
        elem.data['x']-=1.0*mean(elem.data['x'])
        elem.data['y']-=1.0*mean(elem.data['y'])
        elem.data['z']-=1.0*mean(elem.data['z'])
        return

    # We scale the mesh by a factor
    def scale_mesh(self,scale):
        elem=self.get_element_by_name('vertex')[1]
        if isinstance(scale,Iterable):
            elem.data['x']*=scale[0]
            elem.data['y']*=scale[1]
            elem.data['z']*=scale[2]
        else:
            elem.data['x']*=scale
            elem.data['y']*=scale
            elem.data['z']*=scale
        return

    # Recomputing normals
    def recompute_normals(self):
        vertex=self.get_element_by_name('vertex')[1]
        faces =self.get_element_by_name('face')[1]
        vertices=array([[x for x in b] for b in vertex.data])
        s=shape(vertices)
        adds=zeros((s[0],3))
        for face in faces.data:
            ixes=face[0][:]
            vec=cross(vertices[ixes[2],0:3]-vertices[ixes[0],0:3],vertices[ixes[1],0:3]-vertices[ixes[0],0:3])
            adds[ixes,0:3]+=ones((3,1))*vec
        adds/=linalg.norm(adds,axis=1,keepdims=1)*ones((1,3))

        vertex.data['nx']=adds[:,0]
        vertex.data['ny']=adds[:,1]
        vertex.data['nz']=adds[:,2]
        return

    def fix_face_normals(self,*args):
        # We check if normals are directed in the right direction
        # For some reason, the right direction seem to be the inside
        # @TODO : check what is the recommended orientation
        if len(args)==0:
            orientation=+1
        else:
            try:
                orientation=float(args[0])
            except:
                raise ValueError('Errpr : could not understand orientation from %s' % orientation)
        self.recompute_normals()
        vertex=self.get_element_by_name('vertex')[1]

        vertices=array([[x for x in b] for b in vertex.data])
        pts=vertices[:,0:3]
        for i in range(3):
            pts[:,i]-=mean(vertices[:,i])
        norms=vertices[:,3:6]
        sum_o=sum(norms*pts)
        if (sum_o*orientation)<0.0:
            print('Warning : inverted normals ; fixing it.')
            self.invert_faces()
            self.recompute_normals()
        return

    def invert_faces(self):
        # Inverting faces from facing outwards to facing inwards
        vertex=self.get_element_by_name('vertex')[1]
        faces =self.get_element_by_name('face')[1]
        vertices=array([[x for x in b] for b in vertex.data])
        s=shape(vertices)
        # we just reorder the vertices in a face
        for i,face in enumerate(faces.data):
            ixes=face[0][:]
            ixes[2],ixes[1]=ixes[1],ixes[2]
            for j,ix in enumerate(ixes):
                faces.data[i][0][j]=ix
        return

    def add_thickness(self,thickness):
        # We add a thickness : point = point + thickness*normal
        vertex=self.get_element_by_name('vertex')[1]
        vertices=array([[x for x in b] for b in vertex.data])
        try:
            vertices[:,0:3]+=vertices[:,3:6]*thickness
            vertex.data['x']=vertices[:,0]
            vertex.data['y']=vertices[:,1]
            vertex.data['z']=vertices[:,2]
        except:
            raise ValueError("Issue in adding thickness : Could not translate points by normal*thickness")
        return

    def align_mesh(self):
        # We align the mesh to the x axis
        vertex=self.get_element_by_name('vertex')[1]
        vertices=array([[b[i] for i in range(3)] for b in vertex.data])
        pca = PCA(n_components=3)
        vertices=pca.fit_transform(vertices)
        vertex.data['x']=vertices[:,0]
        vertex.data['y']=vertices[:,1]
        vertex.data['z']=vertices[:,2]
        return

    def set_mesh_length(self,length):
        # First we align the data with the x axis
        vertex=self.get_element_by_name('vertex')[1]
        vertices=array([[b[i] for i in range(3)] for b in vertex.data])
        pca = PCA(n_components=3)
        vertices=pca.fit_transform(vertices)
        # then we find the scale
        scale=length/(max(vertices[:,0])-min(vertices[:,0]))
        self.scale_mesh(scale)
        return

    def print_ply_info(self):
        vertex=self.get_element_by_name('vertex')[1]
        vertices=array([[b[i] for i in range(3)] for b in vertex.data])
        for i in range(3):
            print("lengths on axis %s : %s" %(i,(max(vertices[:,i])-min(vertices[:,i]))))
        return


    def change_face_dtype_to_int(self):
        # This fixes an issue of meshlab being sensitive to seeing uint for faces
        # Not necessary
        for face_type in ['face','tetrahedra']:
            try:
                elem=self.get_element_by_name(face_type)[1]
                for i in range(elem.count):
                    elem.data[i][0].dtype=dtype('int32')
                # Necessary
                elem.properties[0].len_dtype='i4'
                elem.properties[0].val_dtype='i4'
            except:
                print('Could not fixuint for all types')
        return

# ------------------------------------------------********
## END OF CLASS MESH                                ****
# ------------------------------------------------********

# --------------------------------------------------------
## General use functions
# --------------------------------------------------------
# Not in the class mesh because they have a wider use

def check_indices(plydata):
    nv=plydata['vertex'].count
    faces=array([[x[0][0],x[0][1],x[0][2]] for x in plydata['face'].data])
    ixes=unique(faces[:,0:3])
    if amin(ixes)>0:
        print('Warning : indices starting at %s > 0' %int(amin(ixes)) )
    if len(ixes) != nv:
        print('Warning : %s vertices but %s referenced in faces' %(int(nv),int(len(ixes))))
    return plydata

def load_ply(fname_in):
    try:
        plydata = PlyData.read(fname_in)
    except:
        raise ValueError('Could not read file %s' %fname_in)
    return plydata


def create_plydata(items,dict_values):
    # @WARNING : Still limited to Vertices and triangles
    if dict_values['Dimension']!=3:
        raise ValueError('Currently not supporting non-2D vertices')
    translations={"Vertices":"vertex", "Triangles":"face", "Tetrahedra" : "tetrahedra"}
    elements=[]
    keys=items.keys()

    for key in keys:
        if dict_values[key]>0:
            Values=items[key]
            name=translations.setdefault(key,"")
            if name=="vertex":
                face=array([(V[0],V[1],V[2],0,0,0) for V in Values],dtype=[('x','f4'),('y','f4'),('z','f4'),('nx','f4'),('ny','f4'),('nz','f4')])
                elements.append(PlyElement.describe(face,name))
                #print(vertex)
            elif name=="face":
                face=array([([T[0],T[1],T[2]],) for T in Values],dtype=[('vertex_index','i4',(3,))])
                elements.append(PlyElement.describe(face,name))
            elif name=="tetrahedra":
                face=array([([T[0],T[1],T[2],T[3]],) for T in Values],dtype=[('vertex_index','i4',(4,))])
                elements.append(PlyElement.describe(face,name))

    return PlyData(elements)

def load_mesh(fname_in,args):
    # Loading from a .mesh file
    # Ok this is a very custom script, it would be better to use a module
    klist=['Vertices','Triangles','Tetrahedra']
    print('Warning : .mesh file reading is still experimental')
    print('Warning : Labels have to be added in command line : label=X')
    print('Warning : now supporting only keys : %s' %(' '.join([k for k in klist])))
    lines=sio.clean_lines(sio.getlines(fname_in))
    keys=['Dimension','Vertices','Edges','Triangles','Tetrahedra','Quadrilaterals','Geometry','CrackedEdges','End']
    dict_lines={}
    dict_lines_nb={}
    dict_values={'Dimension' : 3,'Tetrahedra' : 0, 'Triangles ' : 0}
    check_for_number=False
    key_checked=''
    dict_lines['End']=len(lines)
    # First we parse all lines to get a map of the file organization
    for i,line in enumerate(lines):
        # We check for a number if possible
        # We check for all the keys
        if key_checked=="End":
            dict_lines[key]=i
            break
        if check_for_number:
            words=clean_word_list(line.split(' '))
            try:
                dict_values[key_checked]=int(words[-1])
                dict_lines_nb[key]=i
                check_for_number=False
                #print('Expecting %s elements of type %s' %(dict_values[key_checked],key_checked))
            except:
                raise ValueError('Could not find number for key %s' %key_checked)
        else:
            for key in keys:
                if line.find(key)>=0:
                    dict_lines[key]=i
                    words=clean_word_list(line.split(' '))
                    try:
                        dict_values[key]=int(words[-1])
                        dict_lines[key]=i
                    except:
                        #we except next line to countain a number
                        check_for_number=True
                        key_checked=key
                    break

    # Creating Vertices & Triangles
    items={}
    for k in klist:
        if dict_values[k]>0:
            first_line=dict_lines_nb[k]+1
            last_line=min([dict_lines.setdefault(key,0) for key in keys if dict_lines.setdefault(key,0)>first_line])
            (item,nl,nc)=getdata_lines(lines[first_line:last_line])
            # Mesh have an index starting at 1 while ply start at 0, or something like that
            if k =="Triangles":
                item[:,0:3]-=1
            if k =="Tetrahedra":
                item[:,0:4]-=1
            if nl!=dict_values[k]:
                print('Warning between expected number %s and number of lines %s for key %s' %(dict_values[k],nl,k))
                dict_values[k]=nl
            items[k]=item

    # We can also select a submesh for thick meshes
    select=False
    for arg in args:
        if arg.startswith('submesh='):
            select=True
            choice=arg[8:]
    if select:
        items=keep_submesh(items,choice)
        for k in klist:
            dict_values[k]=len(items[k])

    # Ok should be done now
    plydata=create_plydata(items,dict_values)
    return plydata

def keep_submesh(items,choice):
    # Keeping a submesh from a .mesh file
    # for now only support by label
    # @TODO : support inside, outside
    triangles=items['Triangles']
    try:
        label=int(choice)
    except:
        raise ValueError('Could not understand submesh from %s. Expecting a label number' % choice)

    item=array([triangle for triangle in triangles if triangle[3]==label])

    if 0:
        ixes=unique(item[:,0:3])
        ixes=ixes.astype(int)
        #Now we should keep only vertices corresponding to a chose item
        vertices=items['Vertices']
        vertices=vertices[ixes]
        items['Vertices']=vertices
        item=recompute_indices(item,ixes)
        items['Triangles']=item
    else:
        items['Triangles']=item

    return items

def recompute_indices(item,ixes):
    ixmin=amin(ixes)
    ixmax=amax(ixes)
    count=ixmax-ixmin+1
    if count==len(ixes):
        item[:,0:3]-=ixmin
    else:
        raise ValueError('Non-contiguous blocks not yet implemented')

    return item

def load_from_file(fname_in,args):
    if fname_in.endswith('.ply'):
        plydata=load_ply(fname_in)
    elif fname_in.endswith('.mesh') or fname_in.endswith('.msh'):
        plydata=load_mesh(fname_in,args)
    else:
        raise ValueError('Could not load a mesh from file %s' %fname_in)
    return plydata

def write_ply_to_file(plydata,args):
    check_indices(plydata)
    for arg in args:
        if arg.startswith("out="):
            arg=arg[4:]
            if arg.endswith(".mesh"):
                write_mesh_file(plydata,arg,args)
            if arg.endswith(".ply"):
                write_ply_file(plydata,arg)
    return 0

def write_ply_file(plydata,fname_out):
    plydata.write(fname_out)


def write_mesh_file(plydata,fname_out,args):
    label="1"
    for arg in args:
        if arg.startswith("label="):
            label=arg[6:]
    nv=plydata['vertex'].count
    nf=plydata['face'].count
    out=open(fname_out,'w')
    # Header
    out.write("MeshVersionFormatted  1 \n")
    out.write("Dimension \n 3 \n")
    # Writting the data
    out.write("Vertices \n       %s \n" %nv)
    [out.write(" %s %s %s   0\n" %( x[0],x[1],x[2])) for x in plydata['vertex'].data ]
    out.write("Triangles \n         %s \n" %nf)
    # Remember that .mesh files start counting indices at 1 rather than 0 for ply files
    [out.write("         %s         %s         %s         %s\n" %(x[0][0]+1,x[0][1]+1,x[0][2]+1,label)) for x in plydata['face'].data ]
    if 'tetrahedra' in plydata:
        out.write("Tetrahedra \n         %s \n" %nf)
        # Remember that .mesh files start counting indices at 1 rather than 0 for ply files
        [out.write("         %s         %s         %s         %s \n" %(x[0][0]+1,x[0][1]+1,x[0][2]+1,x[0][3]+1)) for x in plydata['tetrahedra'].data ]
    out.write('End \n')
    out.close()
    return 0

# --------------------------------------------------------
## Specific functions doing that job for main
# --------------------------------------------------------
def main(args):
    options=[]
    inputs=[]
    for arg in args:
        if arg.startswith('-'):
            options.append(arg)
        elif arg.find('=')>0:
            options.append(arg)
        else:
            inputs.append(arg)
    if len(inputs)==1:
        args=inputs+options
        do_mesh_conversion(args)
    else:
        do_batch_conversion(options,files=inputs)

# __main__ or do_batch_conversion calls to this function
def do_mesh_conversion(args):
    # @WARNING : still in development
    #               Most things are not properly verified
    nargs=len(args)
    if nargs<2:
        raise ValueError('Not enough input arguments')
    else:
        fname_in=args[0]
        if nargs>1:
            args=args[1:]
        else:
            args=[]

    # Loading the input
    mesh=Mesh(fname_in,args)
    mesh.initialize()
    mesh.do_mesh_processing()
    return mesh.write_to_file()

##  Batch conversion of mesh files
def do_batch_conversion(args,files=[]):
    # First we check output
    sout=".ply"
    outs=[]
    # Then we check input
    batches=[]
    prefix=''
    suffix=''
    recursive=False
    includes=[]
    excludes=[]
    pathes=[]

    for arg in args:
        if arg.startswith('out='):
            outs.append(arg[4:])
        if arg.startswith('batch='):
            batches.append(arg[6:])
        elif arg.startswith('prefix='):
            prefix=arg[7:]
        elif arg.startswith('suffix='):
            suffix=arg[7:]
        elif arg.startswith('-recurs'):
            recursive=True
        elif arg.startswith('include='):
            includes.append(arg[8:])
        elif arg.startswith('exclude='):
            excludes.append(arg[8:])
        if arg.startswith('path='):
            pathes.append(arg[5:])

    if len(outs)>0:
        sout=outs[0]
        if not sout.startswith('.'):
            raise ValueError('Output argument should be a file format in batch mode')
        if len(outs)>1:
            print('Warning : several output specified, keeping %s ' %sout)
    #else:
    #    print('Warning : replacing files')

    #if len(batch)>1:
    #    raise ValueError('Currently only a single batch job is supported !')
    #batch=batch[0]
    for batch in batches:
        if not batch.startswith('.'):
            raise ValueError('batch= argument should be a file format, e.g. batch=.ply')

    if len(batches)>0:
        if not recursive:
            # Do we have a path ? If not, path is here.s
            if len(pathes)==0:
                pathes=['.']
            for pathe in pathes:
                # Now listing all files in path that match a batch suffix
                for fname in listdir(pathe):
                    if len(fname) > 4:
                        if fname[-4:] in batches:
                            files.append(path.join(pathe,fname))
        else:
            files = sio.make_recursive_file_list(include=includes, exlude=excludes, folders=pathes, ext=batches )

    for file in files:
        if len(sout)==0:
            out=file
        else:
            #out="%s%s%s%s" %(prefix,file.split(batch)[0],sout,suffix)
            name=path.basename(file)
            pathe=path.dirname(file)
            rename = "%s%s%s%s" % (prefix, name.split('.')[0], sout, suffix)
            out = path.join(pathe,rename)

        # this is proper way to copy.
        newargs=args[:]
        newargs.append("out=%s" %out )
        newargs.insert(0,file)
        do_mesh_conversion(newargs)

    # Done
    return len(files)


if __name__ == "__main__":
    args=sys.argv[1:]
    main(args)

