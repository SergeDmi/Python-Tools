#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright Serge Dmitrieff
# www.biophysics.fr
#


"""
# SYNOPSIS

   generic_shooting is a package implemeting linear shooting method in N dimension

# DESCRIPTION

   just a simple yet flexible implementation

# SYNTAX

   shooter(error_function=function_handle,initial_parameters=X,epsilons=dX,conditions=function_handle, **kwargs)


# OPTIONS

    initial_parameters : initial parameters to shoot from
    error_function : handle to a function computing the error from parameters
    epsilons : discrete parameter step to compute the error gradient
    force_parameters : handle to a function(parameters,errors) that can rectify parameter (e.g. keep within range)
    conditions : handle to a function estimating convergence
    thresholds : maximal absolute value of the errors (only if conditions is not defined)
    damping : sets convergence speed. Default : 1. values <1 are not advised.
                damping can also be the handle of a function(parameters,errors)
    n_jobs : defines the number of jobs assigned
                warning : using multiprocessing is slow, use only if compute_errors is slow (e.g a PDE integration)
    task : defines the problem to solve (shoot or extremize)

# EXAMPLE

    # Finding the zero of a parabolic equation :
    error_f=lambda x: x**3 + x**2 - 2*x
    shooting_problem=Shooter(error_function=error_f,initial_parameters=[2,3],epsilons=[0.001,0.001],thresholds=[0.0001,0.00001])
    shooting_problem.solve()
    print(shooting_problem.parameters)

    # Minimizing or maximizing an equation :
    input={"error_function" : lambda x : sum(x*x),
                "initial_parameters" : [1,2] , "epsilons" : [0.0001,0.001],
                 "conditions" : lambda x : abs(x)>0.000001, "task" : "minimize"}
    shooting_problem=Shooter(**input)
    shooting_problem.solve()
    print(shooting_problem.extremum)

"""
#@TODO : Lots of stuff, for instance damping as an array

import types
from numpy import *
MULTIPROCESSING=1
try:
    # We might want to use ThreadPool as the computations might need to call threads/processes themselves
    from pathos.multiprocessing import ThreadPool as Pool
except:
    MULTIPROCESSING=0

STATUS_DICTIONARY={'Not started' : 0, 'Success' : 1, 'Singular Jacobian' : -1, 'Exceeded count'  : -2 }

class Shooter():
    # Shooter is a class implementing a linear shooting method
    def __init__(self, error_function=None,task="shoot",step_size=None, max_step_size=None,
                    initial_parameters=[0], epsilons=[1],
                    conditions=None,thresholds=None,
                    force_parameters=None,max_n_steps=Inf,verbose=0,
                    damping=1.0,n_jobs=1,**kwargs):

        if error_function is None:
            error_function=self.void_function
            print('Warning : no error function provided ; using default linear function')
        # Function that evaluates the error for a parameter set
        self.error_function=error_function
        # Conditions for which we keep on integrating
        self.conditions=conditions
        self.task=task
        self.status=0
        self.max_n_steps=max_n_steps
        self.verbose=verbose

        if task=="minimize" or task=="maximize" or task=="extremize":
            self.integral_function=self.error_function
            self.error_function=self.compute_derivative(self.integral_function)
            if step_size is not None:
                self.step_size=step_size
            elif task != "extremize":
                raise ValueError('Error :  to maximize or minimize a function, you must provide a gradient descent step_size')

        # How many jobs (if multiprocessing)
        self.n_jobs=n_jobs

        if max_step_size is not None:
            self.limit=lambda dF : self.limit_step_size(dF,max_step_size)
        else:
            self.limit=lambda x: x

        # Damping can be a function or a value
        if isinstance(damping,types.FunctionType):
            self.damping=lambda pars,errs,dF : self.limit(damping(pars,errs,dF))
        else:
            try:
                assert(damping>0)
                self.damping=lambda pars,errs,dF : self.limit(dF/damping)
            except:
                raise ValueError('Unrecognized input type for damping : should be function or a scalar >0 ')


        # Function handle : returns corrected parameters
        self.force_parameters=force_parameters

        # Setting parameters
        if isinstance(initial_parameters,list):
            initial_parameters=array(initial_parameters)
        self.initial_parameters=initial_parameters
        self.parameters=initial_parameters
        self.n_params=len(initial_parameters)


        # Discrete step to compute Grad(error)
        if isinstance(epsilons,list):
            epsilons=array(epsilons)
        self.epsilons=epsilons

        # Threshold to keep integrating (if condition function not defined)
        if isinstance(thresholds,list):
            thresholds=array(thresholds)
        self.thresholds=thresholds
        #Preparing variables
        self.make_epsilons()

        # If the success condition is not given by a handle, we make a handle if possible
        if self.conditions==None:
            try:
                self.conditions=self.threshold_function(thresholds)
            except:
                raise ValueError('Error : conditions or thresholds should be defined')

        # If multiprocessing
        # Warning, multiprocessing has a lot of overhead
        #           use only if error_function is **SUPER** slow (seconds)
        if self.n_jobs>1:
            if MULTIPROCESSING==0:
                print("Warning : multiprocessing unavailable")
                self.n_jobs=1

        if self.n_jobs>1:
            self.prepare_pool()


    ## Class methods

    # Solving for the current state
    def solve(self):
        self.compute_current()
        [self.parameters,self.errors,self.criteria,self.status,count]=self.shoot(self.parameters,self.errors)
        if self.task=="minimize" or self.task=="maximize" or self.task=="extremize":
            self.extremum=self.integral_function(self.parameters)
        return count

    # Solving for given parameters and errors
    def shoot(self,parameters,errors):
        count=0
        criteria=self.compute_criteria(errors)
        status=0
        # As long as one criterion imposes, we refine the solution
        while any(criteria) and status>=0 and count<self.max_n_steps:
            #if self.verbose>0:
            #    print('# parameters : %s' % parameters)

            [parameters,status]=self.step_shoot(parameters,errors)

            if status>=0:
                if self.force_parameters is not None:
                    parameters=self.force_parameters(parameters,errors)
                errors=self.compute_errors(parameters)
                criteria=self.compute_criteria(errors)
                count+=1
        if count>=self.max_n_steps:
            status=-2
            print('Warning : exceeded maximum step number')
        return parameters,errors,criteria,status,count

    # One step of the shooting method
    def step_shoot(self,parameters,errors):
        status=1
        if self.n_jobs==1:
            d_errors=array([self.compute_errors(parameters+d_param) for d_param in self.mat_epsilons])
        else:
            d_errors=array(self.pool.map(self.compute_errors, [parameters+d_param for d_param in self.mat_epsilons]))

        Jacobian=array([(error_col - errors)/self.epsilons[i] for i,error_col in enumerate(d_errors)])

        try:
            dF=-linalg.solve(Jacobian,errors)
        except:
            status=-1
            print('Warning : solver stopped : singular matrix')

        if status>0:
            [parameters,status]=self.compute_new_parameters(parameters,errors,dF,status)

        return parameters,status

    # Computes updated parameters
    def compute_new_parameters(self,parameters,errors,dF,status):
        if self.task=="maximize":
            if dot(dF,errors)<=0:
                dF=+errors*self.step_size/linalg.norm(errors)
        elif self.task=="minimize":
            if dot(dF,errors)>=0:
                dF=-errors*self.step_size/linalg.norm(errors)

        d_pars=self.damping(parameters,errors,dF)
        return parameters+d_pars,status

    # Computes the current state
    def compute_current(self):
        self.errors=self.compute_errors(self.parameters)
        self.criteria=self.compute_criteria(self.errors)

    # Prepares a pool of workers
    def prepare_pool(self):
        self.pool=Pool(self.n_jobs)
        return

    # Prepares the array of perturbations to compute the gradient
    def make_epsilons(self):
        self.mat_epsilons=zeros((self.n_params,self.n_params))
        for i in range(self.n_params):
            self.mat_epsilons[i,i]=self.epsilons[i]
        return

    # Wrapper for the error function
    def compute_errors(self,parameters):
        #print("# ---- got parameters: %s" % parameters)
        #print(self.error_function)
        #print("# ---- got errors: %s" % errors)
        #print("parameters : %s ---- error : %s" %(parameters,errors))
        #return errors
        return self.error_function(parameters)

    # Computes the criteria from errors
    def compute_criteria(self,errors):
        return self.conditions(errors)

    # If we try to maximize a function F, the error function is the derivative of F
    def compute_derivative(self,func):
        # Notice that this is a very inefficient way to maximize as many things will be computed twice for no obvious benefit
        return lambda x : self.column_derivatives(func,x)

    # Helper function to compute derivative faster
    def column_derivatives(self,func,x):
        Fx=func(x)
        return array([squeeze((func(x+d_param)-Fx)/(self.epsilons[i])) for i,d_param in enumerate(self.mat_epsilons)])

    ## Generic helper functions
    # Any function ; meant to test the program
    def void_function(self,x):
        return x

    def above_threshold(self,x,x0):
        if len(x)==1:
            return abs(x)>x0
        else:
            return [abs(x)>x0]

    def threshold_function(self,x0):
        return lambda x:self.above_threshold(x,x0)

    def limit_step_size(self,dF,max_step_size):
        step=linalg.norm(dF)
        if any(step>max_step_size):
            if self.verbose:
                print('Warning : limiting step size ')
            return dF*max_step_size/step
        else:
            return dF
