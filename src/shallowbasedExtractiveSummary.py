import sys
import re
import fio
import xml.etree.ElementTree as ET
from collections import defaultdict
from Survey import *
import random
import NLTKWrapper
import singledocumentsummarization
import porter

stopwords = [porter.getStemming(line.lower().strip()) for line in fio.readfile("../../ROUGE-1.5.5/data/smart_common_words.txt")]
print "stopwords:", len(stopwords)

stopwords = stopwords + ['.', '?', '-', ',', '[', ']', '-', ';', '\'', '"', '+', '&', '!', '/', '>', '<', ')', '(', '#', '=']

StemFlag = True

def getKeyNgram(student_summaryList, remove_stop = False, N = 5, weighted = False, M=1, save2file=None, cutoff=1):
    #K is the number of words to be extracted
    #N is the max number of Ngram
    key_ngrams = []
    
    Ndict = defaultdict(float)
    dict = defaultdict(float)
    for n in range(M, N+1):
        for summary in student_summaryList:
            if StemFlag:
                summary = porter.getStemming(summary)
                
            ngrams = NLTKWrapper.getNgram(summary, n)
            for ngram in ngrams:
                ngram = ngram.lower()
                if n==1:
                    if ngram in stopwords: continue
                skip = False
                for stopword in stopwords:
                    if ngram.startswith(stopword + " "):
                        #print "skip:", ngram 
                        skip = True
                        break
                if skip: continue
                    
                if weighted:
                    dict[ngram] = dict[ngram] + n
                else:
                    dict[ngram] = dict[ngram] + 1
                Ndict[ngram] = n
    
    for k,v in dict.items():
        if v < cutoff:
            del dict[k]
        
    return dict
            
def getKeyPhrases(student_summaryList, method='ngram', save2file=None, cutoff=1):
    if method == 'ngram':
        return getKeyNgram(student_summaryList, remove_stop = False, save2file=save2file)
    if method == 'unigram':
        return getKeyNgram(student_summaryList, remove_stop = False, N=1, save2file=save2file)
    if method == 'weightedngram':
        return getKeyNgram(student_summaryList, remove_stop = False, N=5, weighted = True, save2file=save2file)
    if method == "bigram":
        return getKeyNgram(student_summaryList, remove_stop = False, N=2, weighted = False, M=2, save2file=save2file)
    if method == 'ngram_remove_stop':
        return getKeyNgram(student_summaryList, remove_stop = True, save2file=save2file)
    if method == 'unigram_remove_stop':
        return getKeyNgram(student_summaryList, remove_stop = True, N=1, save2file=save2file, cutoff=cutoff)
    if method == 'weightedngram_remove_stop':
        return getKeyNgram(student_summaryList, remove_stop = True, N=5, weighted = True, save2file=save2file)
    if method == "bigram_remove_stop":
        return getKeyNgram(student_summaryList, remove_stop = True, N=2, weighted = False, M=2, save2file=save2file)
    
    return None

def getSentenceScore(sentence, dict):
    if StemFlag:
        sentence = porter.getStemming(sentence)
                
    words = NLTKWrapper.getNgram(sentence, 1)
    s = 0
    
    for word in words:
        if word in dict:
            s = s + dict[word]
    return s
                               
def getShallowBasedExtrativeSummary(student_summaryList, method, K=3, save2file = None):
    dict = getKeyPhrases(student_summaryList, method=method, cutoff=2)
    if save2file != None:
        fio.SaveDict(dict, save2file, SortbyValueflag = True)
    
    Summary = []
    
    selected = [False]*len(student_summaryList)
    
    #greedy algorithm
    for i in range(K):
        maxScore = 0
        maxS = -1
        for k, sentence in enumerate(student_summaryList):
            if selected[k]: continue
            score = getSentenceScore(sentence, dict)
            if score > maxScore:
                maxS = k
                maxScore = score
                
        if maxS != -1:
            sentence = student_summaryList[maxS]
            Summary.append(sentence)
            selected[maxS] = True
            
            #reset the word core
            if StemFlag:
                sentence = porter.getStemming(sentence)
                        
            words = NLTKWrapper.getNgram(sentence, 1)
            for word in words:
                if word in dict:
                    dict[word] = 0
    
    return Summary

def WriteSummary(excelfile, folder, method):
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
            
            Summary = getShallowBasedExtrativeSummary(student_summaryList, method, save2file=filename + ".keys")
            fio.savelist(Summary, filename)
                                    
def ShallowBasedExtrativeSummary(excelfile, datadir, K=30, method='ngram'):
    WriteSummary(excelfile, datadir, method)
    WriteTASummary(excelfile, datadir)
      
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    datadir = "../../mead/data/ShallowbasedExtrativeSummary_unigram/"  
    fio.deleteFolder(datadir)
    ShallowBasedExtrativeSummary(excelfile, datadir, K=30, method='unigram_remove_stop')
#  
#     datadir = "../../mead/data/ShallowSummary_weightedngram_remove_stop/"  
#     fio.deleteFolder(datadir)
#     ShallowSummary(excelfile, datadir, K=30, method='weightedngram_remove_stop')
#      
#     datadir = "../../mead/data/ShallowSummary_bigram_remove_stop/"  
#     fio.deleteFolder(datadir)
#     ShallowSummary(excelfile, datadir, K=30, method='bigram_remove_stop')
    