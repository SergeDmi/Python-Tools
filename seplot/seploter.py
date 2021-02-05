#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright Serge Dmitrieff
# www.biophysics.fr
#
# Based on Python Pyx
import sys

from seplot.seplot import Splotter



if __name__ == "__main__":
    """ Just a script to bridge the module and the executable """
    nargs=len(sys.argv)
    dargs=sys.argv[1:]

    seplot=Splotter(arguments=dargs)
    seplot.make_and_save()
