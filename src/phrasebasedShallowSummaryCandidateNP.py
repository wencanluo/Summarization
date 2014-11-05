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
import postProcess
import phrasebasedShallowSummaryWeighting

import MaximalMatchTokenizer

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
                    
def getKeyNgram(student_summaryList, phrasefile, save2file=None, soft = True, np="candidatestemming"):
    np_phrase = defaultdict(float)
    
    stemdict = {}
    
    #get NP phrases
    for s in student_summaryList:
        if np== "candidate":
            NPs = MaximalMatchTokenizer.MaximalMatchTokenizer(s, phrasefile, stemming=False)
        elif np == 'candidatestemming':
            NPs = MaximalMatchTokenizer.MaximalMatchTokenizer(s, phrasefile)
        elif np == "candidatengram":
            NPs = MaximalMatchTokenizer.NgramMatchTokenizer(s, phrasefile, stemming=False)
        elif np == "candidatengramstemming":
            NPs = MaximalMatchTokenizer.NgramMatchTokenizer(s, phrasefile)
        else:
            NPs = []
            
        for NP in NPs:
            NP = NP.lower()
            
            if soft:
                #cache the stem dictionary
                if NP not in stemdict:
                    stemdict[NP] = getStemDict(NP)
                
                print "----------------------------------"
                print "current dict:"
                fio.PrintDict(np_phrase)
                print "new phrase:" + NP
                
                #update count
                duplicateFlag = False
                for key in np_phrase.keys():
                    overlap_count = getOverlap(stemdict[key], stemdict[NP])
                    if overlap_count >= 1:
                        duplicateFlag = True
                        if NP != key:
                            np_phrase[NP] = np_phrase[NP] + overlap_count
                            np_phrase[key] = np_phrase[key] + overlap_count
                        else:
                            np_phrase[key] = np_phrase[key] + overlap_count
                
                if not duplicateFlag:
                    np_phrase[NP] = np_phrase[NP] + 1
                
            else:
                np_phrase[NP] = np_phrase[NP] + 1
    
    if save2file != None:
        fio.SaveDict(np_phrase, save2file, SortbyValueflag = True)
        
    return np_phrase
            
def getKeyPhrases(student_summaryList, phrasesfile, save2file=None, method="default"):
    return getKeyNgram(student_summaryList, phrasesfile, save2file=save2file, np=method)
                            
def getShallowSummary(excelfile, folder, phrasesdir, K=30, method="default"):
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
            
            phrasefile = phrasesdir + str(week) + ".txt"
            
            Summary = []
            dict = getKeyPhrases(student_summaryList, phrasefile, save2file=filename + ".keys", method=method)
            
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
                        
def ShallowSummary(excelfile, datadir, phrasesdir, K=30, method="default"):
    getShallowSummary(excelfile, datadir, phrasesdir, K, method=method)
    WriteTASummary(excelfile, datadir)
            
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    
    sennadatadir = "../data/senna/"
    phrasesdir = "../data/phrases/"
    outdir = "../data/np/"
    weigthdir = "../data/np/"
    
    #for method in ['default', 'reverser']:
    for method in ['candidate', 'candidatestemming', 'candidatengram', 'candidatengramstemming']:
        datadir = "../../mead/data/ShallowSummary_PhraseCandidateSoft_" + method +"/" 
        #fio.deleteFolder(datadir)
        #ShallowSummary(excelfile, datadir, phrasesdir, K=30, method=method)
   
        #postProcess.ExtractNP(datadir, outdir, method)
        
        for metric in ['npsoft', 'nphard']:
            phrasebasedShallowSummaryWeighting.getNPWeight(weigthdir, metric, method)
             
    print "done"
    