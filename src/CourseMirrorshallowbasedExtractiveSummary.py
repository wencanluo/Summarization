import sys
import re
import fio
import xml.etree.ElementTree as ET
from collections import defaultdict
import CourseMirrorSurvey
import random
import NLTKWrapper
import singledocumentsummarization
import porter

#course = "CS2001"
course = "CS2610"
maxWeekDict = {"CS2610": 5, 
               "CS2001": 1}

maxWeek = maxWeekDict[course]

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
    dict = getKeyPhrases(student_summaryList, method=method, cutoff=1)
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
    sheets = range(0,maxWeek)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        for type in ['POI', 'MP', 'LP']:
            print excelfile, sheet, type
            student_summaryList = CourseMirrorSurvey.getStudentResponseList(excelfile, course, week, type)

            path = folder + str(week)+ '/'
            fio.newPath(path)
            filename = path + type + '.summary'
            
            Summary = getShallowBasedExtrativeSummary(student_summaryList, method, save2file=filename + ".keys")
            
            newSummary = []
            for i, sum in enumerate(Summary):
                newSummary.append('['+str(i+1)+'] ' + sum)
                
            fio.savelist(newSummary, filename)
                                    
def ShallowBasedExtrativeSummary(excelfile, datadir, K=30, method='ngram'):
    WriteSummary(excelfile, datadir, method)
    #WriteTASummary(excelfile, datadir)
      
if __name__ == '__main__':
    excelfile = "../data/CourseMIRROR Reflections.xls"
    datadir = "../../mead/data/"+course+"_ShallowbasedExtrativeSummary_unigram/"  
    fio.deleteFolder(datadir)
    ShallowBasedExtrativeSummary(excelfile, datadir, K=30, method='unigram_remove_stop')
    
    print "done"
    