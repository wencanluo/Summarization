#!/usr/bin/python

#File:
#Functin:
#JSD from website
#http://docs.scipy.org/doc/scipy-dev/reference/generated/scipy.stats.entropy.html
#http://stackoverflow.com/questions/24913425/pythonfast-efficient-implementation-of-the-kullback-leibler-divergence-for-mult?lq=1

import jsd
import util

def JSDDict(dict1, dict2, normalized = False):
    if not normalized:
        dict1 = util.normalize(dict1)
        dict2 = util.normalize(dict2)
    
    keys = set(dict1.keys() + dict2.keys())
    
    vect1 = [dict1[k] if k in dict1 else 0.0 for k in keys]
    vect2 = [dict2[k] if k in dict2 else 0.0 for k in keys]
    
    return jsd.js_div(vect1, vect2)
    
if __name__=="__main__":
     A = {'a':5,'b':3,'c':2}
     B = {'a':4,'d':1,'c':4}
     
     print JSDDict(A, B)
