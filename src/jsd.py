#!/usr/bin/python

#File:
#Functin:
#JSD from website
#http://docs.scipy.org/doc/scipy-dev/reference/generated/scipy.stats.entropy.html
#http://stackoverflow.com/questions/24913425/pythonfast-efficient-implementation-of-the-kullback-leibler-divergence-for-mult?lq=1

import scipy
import numpy as np
from scipy.stats.distributions import entropy

def js_div_matrix(a):
    a=np.array(a)
    W=np.zeros((a.shape[0],a.shape[0]))
    e=-entropy(a.transpose())
    for i in range(a.shape[0]):
        val_range=range(i+1,a.shape[0])
        sumAB=np.tile(a[i,:],(a.shape[0]-i-1,1))+a[val_range,:]
        result=0.5*(e[i]+e[val_range,:]-sum((sumAB)*np.log(((sumAB)/2)),1))
        W[val_range,i]=result
        W[i,val_range]=result
    return W
        
def kl_div(A,B):
    return scipy.stats.entropy(A,B)

def js_div(A,B):
    A = np.array(A)
    B = np.array(B)
    half=(A+B)/2
    return 0.5*kl_div(A,half)+0.5*kl_div(B,half)

if __name__=="__main__":
     A = [0.5,0.3,0.2,0,0.0]
     B = [0.4,0.1,0.4,0.1,0.0]
     print js_div(A,B)
