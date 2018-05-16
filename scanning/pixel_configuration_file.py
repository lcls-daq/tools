#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May  8 14:43:03 2018

@author: blaj
"""

import numpy as np

#test=np.loadtxt('/Volumes/ssd/epix10ka-pulser/autoSwitch.txt',comments='#');
#print 'File shape: %4d,%4d'%test.shape

def pixel_mask(value0,value1,spacing,position):
    ny,nx=352,384;
    if position>=spacing**2:
        print 'position out of range';
        position=0;
    out=np.zeros((ny,nx),dtype=np.int)+value0;
    position_x=position%spacing; position_y=position//spacing;
    out[position_y::spacing,position_x::spacing]=value1;
    return out;

for spacing in [4,5,6,7] :
    for position in range(spacing**2):
        mask=pixel_mask(0,1,spacing,position);
        fname='mask_%02d_%04d.txt'%(spacing,position);
        np.savetxt('epix10ka-pulser/'+fname,mask,fmt='%1d',delimiter=' ');
