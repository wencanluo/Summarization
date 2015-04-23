import sys
import re
import fio
import xml.etree.ElementTree as ET
from collections import defaultdict
import random
import NLTKWrapper
import SennaParser
import porter

import tfidf
import shallowSummary
import phraseClusteringKmedoid

import CourseMirrorSurvey
from CourseMirrorSurvey import maxWeekDict

stopwordfilename = "../../ROUGE-1.5.5/data/smart_common_words.txt"
stopwords = [line.lower().strip() for line in fio.ReadFile("../../ROUGE-1.5.5/data/smart_common_words.txt")]
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
        #NPs = s.getNPrases()
        NPs = s.getSyntaxNP()
        
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
                            
def getShallowSummary(excelfile, folder, sennadatadir, tfidfdir, np, method, K=30):
    sheets = range(0,maxWeek)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        #for type in ['POI', 'MP', 'LP']:
        for type in ['POI', 'MP']:
            print excelfile, sheet, type
            student_summaryList = CourseMirrorSurvey.getStudentResponseList(excelfile, course, week, type, withSource=False)

            path = folder + str(week)+ '/'
            fio.NewPath(path)
            filename = path + type + '.summary'
            
            sennafile = sennadatadir + "senna." + str(week) + "." + type + '.output'
            if not fio.IsExist(sennafile): continue
            
            Summary = []
            
            dict = getKeyPhrases(student_summaryList, sennafile, save2file=filename + ".keys")
            
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
                
                if len(Summary) + 1 <= K:
                #if total_word <= K:
                    Summary.append(key)
            
            fio.SaveList(Summary, filename)
                        
def ShallowSummary(excelfile, datadir, sennadatadir, tfidfdir, np, method, K=30):
    getShallowSummary(excelfile, datadir, sennadatadir, tfidfdir, np, method,  K)

if __name__ == '__main__':
    
    #Step3: extract phrases
    for c in ["PHYS0175", 'IE256']:
        course = c
        maxWeek = maxWeekDict[course]
        
        sennadir = "../data/"+course+"/senna/"
        excelfile = "../data/CourseMirror/Reflection.json"
                
        clusterdir = "../data/"+course+"/np/"
        
        datadir = "../../mead/data/"+course+"_NPSoft/" 
        ShallowSummary(excelfile, datadir, sennadir, tfidfdir=None, np="syntax", method=None, K=4)
        
        import postProcess
        postProcess.ExtractNP(datadir, clusterdir, 'syntax', range(1,40))
    
     
        
    print "done"
    