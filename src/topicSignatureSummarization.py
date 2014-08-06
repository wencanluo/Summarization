from OrigReader import prData
import sys
import re
import fio

from Survey import *
                    
def WriteText(excelfile, datadir):
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
            student_summaryList = [line.strip() + "\n" for line in student_summaryList]
            
            fio.newPath(datadir)
            filename = datadir + str(week) +'_'+ type + '.txt'
            #print filename
            fio.savelist(student_summaryList, filename)
    
def WriteConfig(excelfile, datadir, datadir4topicS, topicS_folder): 
    filename = topicS_folder + 'config_sum.example'
    
    SavedStdOut = sys.stdout
    sys.stdout = open(filename, 'w')
    
    print "stopFilePath = stoplist-smart-sys.txt"
    print "performStemming = N"
    print "backgroundCorpusFreqCounts = bgCounts-Giga.txt"
    print "topicWordCutoff = 1.0"
    
    sheets = range(0,12)
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        for type in ['POI', 'MP', 'LP']:
            textfile = datadir4topicS + str(week) +'_'+ type + '.txt'
            print "inputFile = " + textfile
            
    sys.stdout = SavedStdOut
    
def Write2TopicS(excelfile, datadir, datadir4topicS, topicS_folder):
    WriteText(excelfile, datadir)
    WriteConfig(excelfile, datadir, datadir4topicS, topicS_folder)

def getTopicWords(topicWordsfile, K = 30):
    dict = {}
    for line in fio.readfile(topicWordsfile):
        tokens = line.strip().split()
        assert(len(tokens) == 2)
        dict[tokens[0]] = float(tokens[1])
    
    keys = sorted(dict, key=dict.get, reverse = True)
    
    return keys[0:K]

def getSummary(datadir, summarydir, K):
    sheets = range(0,12)
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        for type in ['POI', 'MP', 'LP']:
            topicSfile = datadir + str(week) +'_'+ type + '.txt.ts'
        
            ts = getTopicWords(topicSfile, K)
            
            path = summarydir + str(week)+ '/'
            fio.newPath(path)
            filename = path + type + '.summary'
            
            fio.savelist(ts, filename)
            
def TopicSignatureSummary(excelfile, datadir, summarydir, K):
    getSummary(datadir, summarydir, K=30)
    WriteTASummary(excelfile, summarydir)
       
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    datadir = "../data/TopicS/"
    datadir4topicS = "../Summarization/data/TopicS/"
    
    topicS_folder = "../../TopicWords-v1/"
    #fio.deleteFolder(datadir)
    Write2TopicS(excelfile, datadir, datadir4topicS, topicS_folder)
    
    summarydir = "../../mead/data/TopicWordStem/"
    fio.deleteFolder(summarydir)
    #TopicSignatureSummary(excelfile, datadir, summarydir, K=30)
    
    #Wrong Mead Summary
    print "done"
    