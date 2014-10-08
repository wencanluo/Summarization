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
import SennaParser

stopwords = [line.lower().strip() for line in fio.readfile("../../ROUGE-1.5.5/data/smart_common_words.txt")]
punctuations = ['.', '?', '-', ',', '[', ']', '-', ';', '\'', '"', '+', '&', '!', '/', '>', '<', ')', '(', '#', '=']

def isMalformed(phrase):
    N = len(phrase.split())
    if N == 1: #single stop words
        if phrase in stopwords: return True
    
    if len(phrase) > 0:
        if phrase[0] in punctuations: return True
    
    return False

def getNPs(sennafile, MalformedFlilter=False):
    np_phrase = []
    
    #read senna file
    sentences = SennaParser.SennaParse(sennafile)
    
    #get NP phrases
    for s in sentences:
        NPs = s.getNPrases()
        
        for NP in NPs:
            NP = NP.lower()
            
            if MalformedFlilter:
                if isMalformed(NP): continue
            
            np_phrase.append(NP)
        
    return np_phrase

def getPhraseClusterAll(sennafile, weightfile, output, ratio=None, MalformedFlilter=False):
    
    NPCandidates = getNPs(sennafile, MalformedFlilter)
    
    NPs, matrix = fio.readMatrix(weightfile, hasHead = True)
    
    #change the similarity to distance
    for i, row in enumerate(matrix):
        for j, col in enumerate(row):
            if matrix[i][j] == "NaN":
                matrix[i][j] = 1.0
            else:
                try:
                    if float(matrix[i][j]) < 0:
                        print "<0", weightfile, i, j, matrix[i][j]
                        matrix[i][j] = 0
                    if float(matrix[i][j]) > 100:
                        print ">100", weightfile, i, j, matrix[i][j]
                        matrix[i][j] = 100
                    matrix[i][j] = 1.0 / math.pow(math.e, float(matrix[i][j]))
                except OverflowError as e:
                    print e
                    exit()

    index = {}
    for i, NP in enumerate(NPs):
        index[NP] = i
    
    newMatrix = []
    
    for NP1 in NPCandidates:
        assert(NP1 in index)
        i = index[NP1]
        
        row = []
        for NP2 in NPCandidates:
            j = index[NP2]
            row.append(matrix[i][j])
            
        newMatrix.append(row)
    
    V = len(NPCandidates)
    if ratio == "sqrt":
        K = int(math.sqrt(V))
    else:
        K = int(ratio*V)
    
    clusterid = ClusterWrapper.KMedoidCluster(newMatrix, K)
     
    body = []   
    for NP, id in zip(NPCandidates, clusterid):
        row = []
        row.append(NP)
        row.append(id)
        body.append(row)    
    
    fio.writeMatrix(output, body, header = None)
    
def getPhraseCluster(phrasedir, method='lexicalOverlapComparer', ratio=None):
    sheets = range(0,12)
    
    for sheet in sheets:
        week = sheet + 1
        for type in ['POI', 'MP', 'LP']:
            weightfilename = phrasedir + str(week)+ '/' + type + '.' + method
            print weightfilename
            
            NPs, matrix = fio.readMatrix(weightfilename, hasHead = True)
            
            #change the similarity to method
            for i, row in enumerate(matrix):
                for j, col in enumerate(row):
                    matrix[i][j] = 1 - float(matrix[i][j]) if matrix[i][j] != "NaN" else 0
            
            V = len(NPs)
            if ratio == None:
                K = int(math.sqrt(V))
            else:
                K = int(ratio*V)
            
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
            
            if ratio == None:    
                file = phrasedir + '/' + str(week) +'/' + type + ".cluster.kmedoids." + "sqrt" + "." +method
            else:
                file = phrasedir + '/' + str(week) +'/' + type + ".cluster.kmedoids." + str(ratio) + "." +method
            fio.writeMatrix(file, body, header = None)
            
#             dict2 = {}
#             for NP, id in zip(NPs, clusterid):
#                 if id not in dict2:
#                     dict2[id] = []
#                 dict2[id].append(NP)
#             
#             header = ['cluster id', 'NPs', 'count']
#             body = []   
#             for id in set(clusterid):
#                 row = []
#                 row.append(id)
#                 row.append(", ".join(dict2[id]))
#                 row.append(dict[id])
#                 
#                 body.append(row)
#             file = phrasedir + '/' + str(week) +'/' + type + ".cluster.kmedoids.count"
#             fio.writeMatrix(file, body, header)
                
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
    
 