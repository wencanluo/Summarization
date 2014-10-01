import sys
import re
import fio
import xml.etree.ElementTree as ET
from collections import defaultdict
from Survey import *
import random
import NLTKWrapper
import SennaParser
import porter
import math
import phrasebasedShallowSummary

import ClusterWrapper

def getPhraseCluster(phrasedir, distance='lexicalOverlapComparer', Kratio=None):
    sheets = range(0,12)
    
    for sheet in sheets:
        week = sheet + 1
        for type in ['POI', 'MP', 'LP']:
            weightfilename = phrasedir + str(week)+ '/' + type + '.' + distance
            print weightfilename
            
            NPs, matrix = fio.readMatrix(weightfilename, hasHead = True)
            
            #change the similarity to distance
            for i, row in enumerate(matrix):
                for j, col in enumerate(row):
                    matrix[i][j] = 1 - float(matrix[i][j]) if matrix[i][j] != "NaN" else 0
            
            V = len(NPs)
            if Kratio == None:
                K = int(math.sqrt(V))
            else:
                K = int(Kratio*V)
            
            K=10    
            clusterid = ClusterWrapper.KMedoidCluster(matrix, K)
            
#             sorted_lists = sorted(zip(NPs, clusterid), key=lambda x: x[1])
#             NPs, clusterid = [[x[i] for x in sorted_lists] for i in range(2)]
            
            dict = defaultdict(int)
            for id in clusterid:
                dict[id] = dict[id] + 1
             
            body = []   
            for NP, id in zip(NPs, clusterid):
                row = []
                row.append(NP)
                row.append(id)
                #row.append(dict[id])
                
                body.append(row)
            
            if Kratio == None:    
                file = phrasedir + '/' + str(week) +'/' + type + ".cluster.kmedoids." + "sqrt" + "." +distance
            else:
                file = phrasedir + '/' + str(week) +'/' + type + ".cluster.kmedoids." + str(Kratio) + "." +distance
            fio.writeMatrix(file, body, header = None)
                
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    
    sennadatadir = "../data/senna/"
    weigthdir = "../data/np/"
    
    #for method in ['nphard', 'npsoft',  'greedyComparerWNLin']:
#     for method in ['greedyComparerWNLin', 'optimumComparerLSATasa','optimumComparerWNLin',  'dependencyComparerWnLeskTanim', 'bleuComparer', 'cmComparer', 'lsaComparer', 'lexicalOverlapComparer']:
#         datadir = "../../mead/data/ShallowSummary_Weighted" + method + '/'
#         fio.deleteFolder(datadir)
#         ShallowSummary(excelfile, datadir, sennadatadir, K=30, weigthdir=weigthdir, method = method)

    phrasedir = "../data/np/"
    
    #for ratio in [None, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    for ratio in [None]:
        #for method in ['greedyComparerWNLin', 'optimumComparerLSATasa','optimumComparerWNLin',  'dependencyComparerWnLeskTanim', 'lexicalOverlapComparer']: #'bleuComparer', 'cmComparer', 'lsaComparer',
        for method in ['lexicalOverlapComparer']:
            getPhraseCluster(phrasedir, method, ratio)
            print method
    
    print "done"
    
 