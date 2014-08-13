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
                    
def getKeyNgram(student_summaryList, sennafile, save2file=None, soft = False):
    np_phrase = defaultdict(float)
    
    #read senna file
    sentences = SennaParser.SennaParse(sennafile)
    
    stemdict = {}
    
    #get NP phrases
    for s in sentences:
        NPs = s.getNPrases()
        
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
            
def getKeyPhrases(student_summaryList, sennafile, save2file=None):
    return getKeyNgram(student_summaryList, sennafile, save2file=save2file)
                            
def getNPList(excelfile, sennadatadir, weigthdir):
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

            path = weigthdir + str(week)+ '/'
            fio.newPath(path)
            filename = path + type + '.key'
            
            sennafile = sennadatadir + "senna." + str(week) + "." + type + '.output'
            dict = getKeyPhrases(student_summaryList, sennafile)
            
            fio.savelist(dict.keys(), filename)

def getNPSort(np1, np2):
    dict1 = getStemDict(np1)
    dict2 = getStemDict(np2)
    
    return getOverlap(dict1, dict2)

def getNPHard(np1, np2):
    if np1 == np2:
        return 1
    else:
        return 0
    
def getNPWeight(weigthdir, method='npsort'):
    #K is the number of words per points
    sheets = range(0,12)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        for type in ['POI', 'MP', 'LP']:
            path = weigthdir + str(week)+ '/'
            fio.newPath(path)
            filename = path + type + '.key'
            NPs = fio.loadlist(filename)
            
            header = NPs
            body = []
            for np1 in NPs:
                row = []
                for np2 in NPs:
                    weight = 0
                    if method == 'npsoft':
                        weight = getNPSort(np1, np2)
                    if method == 'nphard':
                        weight = getNPHard(np1, np2)
                    row.append(weight)
                body.append(row)
            
            
            fio.writeMatrix(path + type + '.' + method, body, header)
                        
def ShallowSummary(excelfile, datadir, sennadatadir, K=30):
    getShallowSummary(excelfile, datadir, sennadatadir, K)
    WriteTASummary(excelfile, datadir)
        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    
    sennadatadir = "../data/senna/"
    weigthdir = "../data/np/"
    
    #datadir = "../../mead/data/ShallowSummary_NPhraseSoft/" 
    datadir = "../../mead/data/ShallowSummary_NPhraseHard/"   
    #fio.deleteFolder(datadir)
    #getNPList(excelfile, sennadatadir, weigthdir)
    getNPWeight(weigthdir, method = 'npsoft')
    getNPWeight(weigthdir, method = 'nphard')
    
    #print getNPSort("help", 'help')
    print 'done'