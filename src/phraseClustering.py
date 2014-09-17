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

import phrasebasedShallowSummary

import ClusterWrapper

K = 10

def toStemMatrix(NPs):
    dicts = []
    
    for NP in NPs:
        dict = phrasebasedShallowSummary.getStemDict(NP)
        dicts.append(dict)
    
    keys = []
    
    for dict in dicts:
        keys = keys + dict.keys()
    
    keys = set(keys)
    
    header = keys
    data = []
    
    for dict in dicts:
        row = [1 if key in dict else 0 for key in keys]
        data.append(row)
        
    return header, data

def getPhraseCluster(phrasedir):
    sheets = range(0,12)
    
    for sheet in sheets:
        week = sheet + 1
        for type in ['POI', 'MP', 'LP']:
            filename = phrasedir + '/' + str(week) +'/' + type + ".key"
            
            NPs = fio.readfile(filename)
            NPs = [NP.strip() for NP in NPs]
            
            header, data = toStemMatrix(NPs)
            
            clusterid, _ = ClusterWrapper.KCluster(data, K)
            
            sorted_lists = sorted(zip(NPs, clusterid), key=lambda x: x[1])
            NPs, clusterid = [[x[i] for x in sorted_lists] for i in range(2)]
            
            dict = defaultdict(int)
            for id in clusterid:
                dict[id] = dict[id] + 1
             
            body = []   
            for NP, id in zip(NPs, clusterid):
                row = []
                row.append(NP)
                row.append(id)
                row.append(dict[id])
                
                body.append(row)
                
            file = phrasedir + '/' + str(week) +'/' + type + ".cluster.kmeans"
            #fio.writeMatrix(file, body, header = None)
            
            dict3 = {}
            for NP, id in zip(NPs, clusterid):
                dict3[NP] = id
            fio.SaveDict(dict3, file)
            
            dict2 = {}
            for NP, id in zip(NPs, clusterid):
                if id not in dict2:
                    dict2[id] = []
                dict2[id].append(NP)
            
            header = ['cluster id', 'NPs', 'count']
            body = []   
            for id in set(clusterid):
                row = []
                row.append(id)
                row.append(", ".join(dict2[id]))
                row.append(dict[id])
                
                body.append(row)
            file = phrasedir + '/' + str(week) +'/' + type + ".cluster.kmeans.count"
            fio.writeMatrix(file, body, header)
                
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
    getPhraseCluster(phrasedir)
    
 