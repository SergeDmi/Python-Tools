#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Serge Dmitrieff
# www.biophysics.fr

# @TODO : different scales on different directions
# @TODO : support for complex mesh (non triangular)
# @TODO : embed in a class !!!!!


"""
# SYNOPSIS

    ply_convert is a command line tool to convert and perform simple tasks on .mesh and .ply files

# DESCRIPTION

    ply_convert reads a mesh from a file (.mesh or .ply), performs simple operations, and saves it (to .mesh or .ply)
    uses the module plyfile : https://github.com/dranjan/python-plyfile/
    Requires the module tools : https://github.com/SergeDmi/Utilities/blob/master/bin/tools.py
    More : https://biophysics.fr

# SYNTAX

   python ply_convert.py INPUT_FILE out=OUTPUT_FILE [OPTIONS] [out=additional_output_file] [ADDITIONAL_OPTIONS]

# OPTIONS

    Options are to be written as opt=value or -option
    Unless mentioned otherwise, options are not applied by default

    Supported options :
        out=            : name of output file
        scale=          : scale to be applied to points
        length=         : length of object on dimension of maximal variance
        thickness=      : adds to each point a vector thickness*normal
        batch=          : apply to all files of a certain type ; overrides INPUT_FILE
        path=           : path in which to look for files for batch operation
        label=          : label of mesh, added when saving mesh files
        orientation=    : orientation of normals (+1 : towards outside, -1 : towards inside)
        -center         : center the data around [0,0,0]
        -align          : aligns data to dimension x
        -normals        : computes normals from faces
        -verbose        : verbose output
        -fixnorms       : makes sure normals are inwards (equivalent to option orientation=-1)
        -fixuint        : fixes format to meshlab-friendly

# EXAMPLES :

            ply_convert.py file.ply out=file.mesh

                        converts a ply file file.ply to a mesh file file.mesh


            ply_convert.py file.mesh normals=1 out=file.ply

                        converts a mesh file to a ply file, and compue the normal at each point


            ply_convert.py file.ply -center -align -normals length=7 -verbose thickness=0.15
                                verbose=1 out=thickened.mesh out=thickened.ply

                        converts a ply file to a ply and a mesh file
                        after centering, aligning, computing normals, scaling the object to a length of 7,
                        and adding an extra thickness of 0.15


            ply_convert.py batch=.ply path='/home/user/simulations/' out='.ply' -fixuint

                        rewrites all the ply files in folder path after fixing the variable type of Vertices
                        Note : useful because tinply (<3) doesn't agree with meshlab (<3) for some reason


"""

####### Python modules
try:
    from numpy import *
    from plyfile import PlyData, PlyElement
    import sys
    from os import listdir
    from sklearn.decomposition import PCA
except:
    raise ValueError('Necessary Python modules could not be loaded')
try:
    from import_tools import *
except:
    print('Warning : import_tools could not be loaded. Get it from https://github.com/SergeDmi/Utilities/blob/master/bin/import_tools.py')
    print('Warning : will not be able to load .mesh files ')


# __main__ calls to this function
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
    plydata=load_from_file(fname_in,args)
    plydata=process_plydata(plydata,args)
    return write_ply_to_file(plydata,args)

##  Batch conversion of mesh files
def do_batch_conversion(args):
    # First we check output
    sout=""
    outs=[args.pop(i) for i,arg in enumerate(args) if arg.startswith('out=')]
    if len(outs)>0:
        sout=outs[0][4:]
        if not sout.startswith('.'):
            raise ValueError('Output argument should be a file format in batch mode')
        if len(outs)>1:
            print('Warning : several output specified, keeping %s ' %sout)
    else:
        print('Warning : replacing files')

    # Then we check input
    batch=[arg[6:] for arg in args if arg.startswith('batch=')]
    if len(batch)>1:
        raise ValueError('Currently only a single batch job is supported !')
    batch=batch[0]
    if not batch.startswith('.'):
        raise ValueError('batch= argument should be a file format, e.g. batch=.ply')

    # Do we have a path ? If not, path is here.
    pathes=[arg[5:] for arg in args if arg.startswith('path=')]
    if len(pathes)>0:
        path=pathes[0]
    else:
        path='.'

    # Now listing all files in path that match batch suffix
    files=[fname for fname in listdir(path) if fname.endswith(batch)]
    for file in files:
        if len(sout)==0:
            out=file
        else:
            out="%s%s" %(file.split(batch)[0],sout)
        # this is proper way to copy.
        newargs=args[:]
        newargs.append("out=%s" %out )
        newargs.insert(0,file)
        do_mesh_conversion(newargs)

    # Done
    return len(files)


def create_plydata(items,dict_values):
    # @WARNING : Still limited to Vertices and triangles
    if dict_values['Dimension']!=3:
        raise ValueError('Currently not supporting non-2D vertices')
    translations={"Vertices":"vertex", "Triangles":"face", "Tetrahedra" : "tetrahedra"}
    elements=[]
    keys=items.keys()
    #print(keys
    for key in keys:
        if dict_values[key]>0:
            Values=items[key]
            name=translations.setdefault(key,"")
            if name=="vertex":
                vertex=array([(V[0],V[1],V[2],0,0,0) for V in Values],dtype=[('x','f4'),('y','f4'),('z','f4'),('nx','f4'),('ny','f4'),('nz','f4')])
                elements.append(PlyElement.describe(vertex,name))
                #print(vertex)
            elif name=="face":
                face=array([([T[0],T[1],T[2]],) for T in Values],dtype=[('vertex_index','i4',(3,))])
                elements.append(PlyElement.describe(face,name))
            elif name=="tetrahedra":
                face=array([([T[0],T[1],T[2]],) for T in Values],dtype=[('tetrahedra_index','i4',(4,))])
                elements.append(PlyElement.describe(face,name))
                #print(face)
    return PlyData(elements)

def load_mesh(fname_in,args):
    klist=['Vertices','Triangles','Tetrahedra']
    print('Warning : .mesh file reading is still experimental')
    print('Warning : Labels have to be added in command line : label=X')
    print('Warning : now supporting only keys : %s' %(' '.join([k for k in klist])))
    lines=getlines(fname_in)
    keys=['Dimension','Vertices','Edges','Triangles','Tetrahedra','Quadrilaterals','Geometry','CrackedEdges','End']
    dict_lines={}
    dict_lines_nb={}
    dict_values={'Dimension' : 3}
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
                print('Expecting %s elements of type %s' %(dict_values[key_checked],key_checked))
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
        first_line=dict_lines_nb[k]+1
        last_line=min([dict_lines.setdefault(key,0) for key in keys if dict_lines.setdefault(key,0)>first_line])
        (item,nl,nc)=getdata_lines(lines[first_line:last_line])
        # Mesh have an index starting at 1 while ply start at 0, or something like that
        if k=="Triangles":
            item[:,0:dict_values['Dimension']]-=1
        if nl!=dict_values[k]:
            raise ValueError('Mismatch between expected number %s and number of lines %s for key %s' %(dict_values[k],nl,k))
        else:
            items[k]=item

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

def center_mesh(plydata):
    plydata['vertex'].data['x']-=1.0*mean(plydata['vertex'].data['x'])
    plydata['vertex'].data['y']-=1.0*mean(plydata['vertex'].data['y'])
    plydata['vertex'].data['z']-=1.0*mean(plydata['vertex'].data['z'])
    return plydata

def scale_mesh(plydata,scale):
    plydata['vertex'].data['x']*=scale
    plydata['vertex'].data['y']*=scale
    plydata['vertex'].data['z']*=scale
    return plydata

def recompute_normals(plydata):
    vertices=array([[x for x in b] for b in plydata['vertex'].data])
    s=shape(vertices)
    adds=zeros((s[0],3))
    for face in plydata['face'].data:
        ixes=face[0][:]
        vec=cross(vertices[ixes[2],0:3]-vertices[ixes[0],0:3],vertices[ixes[1],0:3]-vertices[ixes[0],0:3])
        adds[ixes,0:3]+=ones((3,1))*vec
    adds/=linalg.norm(adds,axis=1,keepdims=1)*ones((1,3))
    #vertices[:,3:6]=adds
    plydata['vertex'].data['nx']=adds[:,0]
    plydata['vertex'].data['ny']=adds[:,1]
    plydata['vertex'].data['nz']=adds[:,2]
    return plydata

def fix_face_normals(plydata,*args):
    # We check if normals are directed in the right direction
    # For some reason, the right direction seem to be the inside
    # @TODO : check what is the recommended orientation
    if len(args)==0:
        orientation=-1
    else:
        try:
            orientation=float(args[0])
        except:
            raise ValueError('Errpr : could not understand orientation from %s' % orientation)
    plydata=recompute_normals(plydata)
    vertices=array([[x for x in b] for b in plydata['vertex'].data])
    pts=vertices[:,0:3]
    for i in range(3):
        pts[:,i]-=mean(vertices[:,i])
    norms=vertices[:,3:6]
    sum_o=sum(norms*pts)
    if (sum_o*orientation)<0.0:
        print('Warning : inverted normals ; fixing it.')
        plydata=invert_faces(plydata)
        plydata=recompute_normals(plydata)
    return plydata

def invert_faces(plydata):
    vertices=array([[x for x in b] for b in plydata['vertex'].data])
    s=shape(vertices)
    for i,face in enumerate(plydata['face'].data):
        ixes=face[0][:]
        ixes[2],ixes[1]=ixes[1],ixes[2]
        for j,ix in enumerate(ixes):
            plydata['face'].data[i][0][j]=ix
    return plydata

def add_thickness(plydata,thickness):
    vertices=array([[x for x in b] for b in plydata['vertex'].data])
    try:
        vertices[:,0:3]+=vertices[:,3:6]*thickness
        plydata['vertex'].data['x']=vertices[:,0]
        plydata['vertex'].data['y']=vertices[:,1]
        plydata['vertex'].data['z']=vertices[:,2]
    except:
        raise ValueError("Issue in adding thickness : Could not translate points by normal*thickness")
    return plydata

def align_mesh(plydata):
    pca = PCA(n_components=3)
    vertices=array([[b[i] for i in range(3)] for b in plydata['vertex'].data])
    vertices=pca.fit_transform(vertices)
    plydata['vertex'].data['x']=vertices[:,0]
    plydata['vertex'].data['y']=vertices[:,1]
    plydata['vertex'].data['z']=vertices[:,2]
    return plydata

def set_mesh_length(plydata,length):
    # First we align the data with the x axis
    pca = PCA(n_components=3)
    vertices=array([[b[i] for i in range(3)] for b in plydata['vertex'].data])
    vertices=pca.fit_transform(vertices)
    # then we find the scale
    scale=length/(max(vertices[:,0])-min(vertices[:,0]))
    return scale_mesh(plydata,scale)

def print_ply_info(plydata):
    vertices=array([[b[i] for i in range(3)] for b in plydata['vertex'].data])
    for i in range(3):
        print("lengths on axis %s : %s" %(i,(max(vertices[:,i])-min(vertices[:,i]))))
    return 0

def load_ply(fname_in):
    try:
        plydata = PlyData.read(fname_in)
    except:
        raise ValueError('Could not read file %s' %fname_in)

    return plydata

def change_face_dtype_to_int(plydata):
    # This fixes an issue of meshlab being sensitive to seeing uint for faces
    # Not necessary
    for i in range(plydata['face'].count):
        plydata['face'].data[i][0].dtype=dtype('int32')
    # Necessary
    plydata['face'].properties[0].len_dtype='i4'
    plydata['face'].properties[0].val_dtype='i4'
    return plydata

def check_indices(plydata):
    nv=plydata['vertex'].count
    faces=array([[x[0][0],x[0][1],x[0][2]] for x in plydata['face'].data])
    ixes=unique(faces[:,0:3])
    if amin(ixes)>0:
        print('Warning : indices starting at %s > 0' %int(amin(ixes)) )
    if len(ixes) != nv:
        print('Warning : %s vertices but %s referenced in faces' %(int(nv),int(len(ixes))))
    return plydata

def process_plydata(plydata,args):
    for arg in args:
        # Centering the data around 0
        if arg.startswith("scale="):
            try:
                scale=float(arg[6:])
                plydata=scale_mesh(plydata,scale)
            except:
                raise ValueError('Could not read from argument scale')

        if arg.startswith("-center"):
            plydata=center_mesh(plydata)

        if arg.startswith("length="):
            length=float(arg[7:])
            plydata=set_mesh_length(plydata,length)

        if arg.startswith("-align"):
            plydata=align_mesh(plydata)

        if arg.startswith("-normal"):
            plydata=recompute_normals(plydata)

        if arg.startswith("-fixnorms") or arg.startswith("-fixnormals"):
            plydata=fix_face_normals(plydata)

        if arg.startswith("orientation="):
            orientation=arg[12:]
            plydata=fix_face_normals(plydata,orientation)

        if arg.startswith("thickness="):
            thickness=float(arg[10:])
            plydata=add_thickness(plydata,thickness)

        if arg.startswith("-verbose"):
            print_ply_info(plydata)

        if arg.startswith("-fixuint"):
            plyadata=change_face_dtype_to_int(plydata)

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
    out.write('End \n')
    out.close()
    return 0

if __name__ == "__main__":
    args=sys.argv[1:]
    # Checking which kind of job we're doing : batch or single
    bb=array([1 for arg in args if arg.startswith('batch=')])
    if sum(bb)>0:
        do_batch_conversion(args)
    else:
        do_mesh_conversion(args)
