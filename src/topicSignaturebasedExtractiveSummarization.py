from OrigReader import prData
import sys
import re
import fio
import shallowbasedExtractiveSummary

from Survey import *
import porter

StemFlag = True

def getTopicWords(topicWordsfile):
    dict = {}
    for line in fio.readfile(topicWordsfile):
        tokens = line.strip().split()
        assert(len(tokens) == 2)
        dict[tokens[0]] = float(tokens[1])
        
    return dict

def getExtrativeSummary(student_summaryList, dict, K=3, save2file = None):
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
            score = shallowbasedExtractiveSummary.getSentenceScore(sentence, dict)
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

def getSummary(excelfile, datadir, summarydir, K):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    sheets = range(0,12)
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            topicSfile = datadir + str(week) +'_'+ type + '.txt.ts'
            student_summaryList = getStudentResponseList(orig, header, summarykey, type)
            
            dict = getTopicWords(topicSfile)

            path = summarydir + str(week)+ '/'
            fio.newPath(path)
            filename = path + type + '.summary'
            summary = getExtrativeSummary(student_summaryList, dict, K, save2file=filename + ".keys")
            
            fio.savelist(summary, filename)
            
def TopicSignatureSummary(excelfile, datadir, summarydir, K):
    getSummary(excelfile, datadir, summarydir, K)
    WriteTASummary(excelfile, summarydir)
       
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    datadir = "../data/TopicS/"
    
    summarydir = "../../mead/data/ShallowbasedExtrativeSummary_topicS/"
    fio.deleteFolder(summarydir)
    TopicSignatureSummary(excelfile, datadir, summarydir, K=3)
    
    #Wrong Mead Summary
    print "done"
    