import sys
import re
import fio
import xml.etree.ElementTree as ET
from collections import defaultdict
from Survey import *
import random
import NLTKWrapper

def getKeyNgram(student_summaryList, K, N = 5, weighted = False, M=1):
    #K is the number of words to be extracted
    #N is the max number of Ngram
    key_ngrams = []
    
    Ndict = defaultdict(float)
    dict = defaultdict(float)
    for n in range(M, N+1):
        for summary in student_summaryList:
            ngrams = NLTKWrapper.getNgram(summary, n)
            for ngram in ngrams:
                ngram = ngram.lower()
                if weighted:
                    dict[ngram] = dict[ngram] + n
                else:
                    dict[ngram] = dict[ngram] + 1
                Ndict[ngram] = n
    keys = sorted(dict, key=dict.get, reverse = True)
    
    fio.SaveDict(dict, "log.txt", SortbyValueflag = True)
    
    total_word = 0
    word_count = 0
    for key in keys:
        word_count = Ndict[key]
        total_word = total_word + word_count
        if total_word <= K:
            key_ngrams.append(key)
        
    return key_ngrams
            
def getKeyPhrases(student_summaryList, K, method='ngram'):
    if method == 'ngram':
        return getKeyNgram(student_summaryList, K)
    if method == 'unigram':
        return getKeyNgram(student_summaryList, K, N=1)
    if method == 'weightedngram':
        return getKeyNgram(student_summaryList, K, N=5, weighted = True)
    if method == "bigram":
        return getKeyNgram(student_summaryList, K, N=2, weighted = False, M=2)
    return None
                            
def getShallowSummary(excelfile, folder, K=30, method='ngram'):
    #K is the number of words per points
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    sheets = range(0,12)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            student_summaryList = getStudentResponseList(orig, header, summarykey, type)

            path = folder + str(week)+ '/'
            fio.newPath(path)
            filename = path + type + '.summary'
            
            longestSummary = []
            
            longestSummary = getKeyPhrases(student_summaryList, K, method)
            
            fio.savelist(longestSummary, filename)
                        

def ShallowSummary(excelfile, datadir, K=30, method='ngram'):
    getShallowSummary(excelfile, datadir, K, method)
    WriteTASummary(excelfile, datadir)

def getStudentResponses4Senna(excelfile, datadir):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    sheets = range(0,12)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            student_summaryList = getStudentResponseList(orig, header, summarykey, type)
            filename = datadir + "senna." + str(week) + "." + type + ".input"
            fio.savelist(student_summaryList, filename)
        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    
    sennadatadir = "../data/senna/"
    
    #getStudentResponses4Senna(excelfile, sennadatadir)
    
    datadir = "../../mead/data/ShallowSummary_ngram/"  
    fio.deleteFolder(datadir)
    ShallowSummary(excelfile, datadir, K=30, method='ngram')
#     
#     datadir = "../../mead/data/ShallowSummary_unigram/"  
#     fio.deleteFolder(datadir)
#     ShallowSummary(excelfile, datadir, K=30, method='unigram')
    
    #datadir = "../../mead/data/ShallowSummary_weightedngram/"  
    #fio.deleteFolder(datadir)
    #ShallowSummary(excelfile, datadir, K=30, method='weightedngram')
    
    #datadir = "../../mead/data/ShallowSummary_bigram/"  
    #fio.deleteFolder(datadir)
    #ShallowSummary(excelfile, datadir, K=60, method='bigram')
    
    