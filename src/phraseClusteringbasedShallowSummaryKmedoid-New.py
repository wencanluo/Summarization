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
import phraseClusteringKmedoid

stopwords = [line.lower().strip() for line in fio.readfile("../../ROUGE-1.5.5/data/smart_common_words.txt")]
print "stopwords:", len(stopwords)

stopwords = stopwords + ['.', '?', '-', ',', '[', ']', '-', ';', '\'', '"', '+', '&', '!', '/', '>', '<', ')', '(', '#', '=']


def getOverlap(dict1, dict2):
    count = 0
    for key in dict1.keys():
        if key in stopwords: 
            continue
        if key in dict2:
            count = count + 1
    return count

def getStemDict(words):
    dict = {}
    stemed = porter.getStemming(words)
    for token in stemed.split():
        dict[token] = 1
    return dict
                    
def getKeyNgram(student_summaryList, sennafile, save2file=None):
    np_phrase = []
    
    #read senna file
    sentences = SennaParser.SennaParse(sennafile)
    
    stemdict = {}
    
    #get NP phrases
    for s in sentences:
        NPs = s.getNPrases()
        
        for NP in NPs:
            NP = NP.lower()
            np_phrase.append(NP)
        
    return np_phrase
            
def getKeyPhrases(student_summaryList, sennafile, save2file=None):
    return getKeyNgram(student_summaryList, sennafile, save2file=save2file)
                            
def getShallowSummary(excelfile, folder, sennadatadir, clusterdir, K=30, method=None, ratio=None):
    #K is the number of words per points
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    sheets = range(0,12)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            print excelfile, sheet, type
            student_summaryList = getStudentResponseList(orig, header, summarykey, type)

            path = folder + str(week)+ '/'
            fio.newPath(path)
            filename = path + type + '.summary'
            
            #produce the cluster file on the fly
            sennafile = sennadatadir + "senna." + str(week) + "." + type + '.output'
            output = clusterdir + str(week) +'/' + type + ".cluster.kmedoids." + str(ratio) + "." +method
            weightfile = clusterdir + str(week)+ '/' + type + '.' + method
            phraseClusteringKmedoid.getPhraseClusterAll(sennafile, weightfile, output, ratio)
            body = fio.readMatrix(output, False)
            
            NPs = [row[0] for row in body]
            
            cluster = {}
            for row in body:
                cluster[row[0]] = int(row[1])
            
            Summary = []
            
            #sort the clusters according to the number of phrases
            dict = defaultdict(float)
            for row in body: 
                dict[int(row[1])] = dict[int(row[1])] + 1
            
            keys = sorted(dict, key=dict.get, reverse =True)
            
            total_word = 0
            word_count = 0
            for key in keys:
                phrase = NPs[key]
                if phrase in Summary: continue
                
                word_count = len(phrase.split())
                total_word = total_word + word_count
                if total_word <= K:
                    Summary.append(phrase)
            
            fio.savelist(Summary, filename)
                        
def ShallowSummary(excelfile, datadir, sennadatadir, clusterdir, K=30, method=None, ratio=None):
    getShallowSummary(excelfile, datadir, sennadatadir, clusterdir, K, method, ratio)
    WriteTASummary(excelfile, datadir)
        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    
    sennadatadir = "../data/senna/"
    clusterdir = "../data/np/"
    
    #for ratio in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    for ratio in ["sqrt", 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        for method in ['npsoft', 'lexicalOverlapComparer','greedyComparerWNLin', 'optimumComparerLSATasa','optimumComparerWNLin',  'dependencyComparerWnLeskTanim']: #'bleuComparer', 'cmComparer', 'lsaComparer',
        #for method in ['dependencyComparerWnLeskTanim']:
        #for method in ['npsoft']:
            datadir = "../../mead/data/ShallowSummary_ClusteringNP_KMedoid_"+str(ratio)+"_"+method+"/"   
            fio.deleteFolder(datadir)
            ShallowSummary(excelfile, datadir, sennadatadir, clusterdir, K=30, method=method, ratio=ratio)
            
    print "done"

    