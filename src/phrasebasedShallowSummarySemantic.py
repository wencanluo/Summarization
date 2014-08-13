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

def getWeight(np1, np2, matrix, headdict):
    
    if np1 not in headdict: return 0
    if np2 not in headdict: return 0
    
    index1 = headdict[np1]
    index2 = headdict[np2]
    return float(matrix[index1][index2])

def getNPDict(student_summaryList, sennafile, save2file=None,  matrix=None, headdict=None):
    np_phrase = defaultdict(float)
    
    #read senna file
    sentences = SennaParser.SennaParse(sennafile)
        
    #get NP phrases
    for s in sentences:
        NPs = s.getNPrases()
        
        for NP in NPs:
            NP = NP.lower()
            
            if NP in np_phrase:
                np_phrase[NP] = np_phrase[NP] + getWeight(NP, NP, matrix, headdict)
            else:
                np_phrase[NP] = np_phrase[NP] + 1
                
            for key in np_phrase.keys():
                if key == NP: continue
                overlap_count = getWeight(key, NP, matrix, headdict)
                np_phrase[NP] = np_phrase[NP] + overlap_count
                np_phrase[key] = np_phrase[key] + overlap_count

    if save2file != None:
        fio.SaveDict(np_phrase, save2file, SortbyValueflag = True)
        
    return np_phrase

                            
def getShallowSummary(excelfile, folder, sennadatadir, K=30, weigthdir = None, method = 'npsoft'):
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
            
            sennafile = sennadatadir + "senna." + str(week) + "." + type + '.output'
            
            #load the weight matrix
            weightfilename = weigthdir + str(week)+ '/' + type + '.' + method
            header, body = fio.readMatrix(weightfilename, hasHead = True)
            headdict = {}
            print len(header)
            print len(body)
            print len(body[0])
            for i,head in enumerate(header):
                headdict[head] = i
            
            Summary = []
            
            dict = getNPDict(student_summaryList, sennafile, save2file=filename + ".keys", matrix=body, headdict=headdict)
                
            keys = sorted(dict, key=dict.get, reverse = True)
            total_word = 0
            word_count = 0
            for key in keys:
                skip = False
                for s in Summary:
                    if getOverlap(getStemDict(s), getStemDict(key)) > 0: #duplicate removing
                        skip = True
                        continue
                if skip: continue
                word_count = len(key.split())
                total_word = total_word + word_count
                if total_word <= K:
                    Summary.append(key)
            
            fio.savelist(Summary, filename)
                        
def ShallowSummary(excelfile, datadir, sennadatadir, K=30, weigthdir = None, method='npsoft'):
    getShallowSummary(excelfile, datadir, sennadatadir, K, weigthdir, method)
    WriteTASummary(excelfile, datadir)
        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    
    sennadatadir = "../data/senna/"
    weigthdir = "../data/np/"
    
    #for method in ['nphard', 'npsoft',  'greedyComparerWNLin']:
    for method in ['greedyComparerWNLin']:
        datadir = "../../mead/data/ShallowSummary_" + method + '/'
        fio.deleteFolder(datadir)
        ShallowSummary(excelfile, datadir, sennadatadir, K=30, weigthdir=weigthdir, method = method)
 