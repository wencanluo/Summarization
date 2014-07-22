from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET
import numpy as np

from Survey import *
                    
def formatSummaryOutput(excelfile, datadir, output):
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    sheets = range(0,12)
    
    datahead = ['Week', '# of sentence POI', '# of sentence POI', '# of sentence POI']
    
    head = ['Week', 'TA:POI', 'TA:MP','TA:LP', 'S:POI', 'S:MP','S:LP',]
    body = []
    
    for sheet in sheets:
        row = []
        week = sheet + 1
        row.append(week)
            
        for type in ['POI', 'MP', 'LP']:
            summaries = getMeadSummary(datadir, type)
            
            orig = prData(excelfile, sheet)
        
            summary = getTASummary(orig, header, summarykey, type)
            if summary == []:
                row.append("")
            else:
                row.append(";".join(summary))
                
            summary = ";".join(summaries[sheet])
            row.append(summary)
        
        body.append(row)
            
    fio.writeMatrix(output, body, head)

def GetRougeScore(datadir, output):
    sheets = range(0,11)
    types = ['POI', 'MP', 'LP']
    scores = ['ROUGE-2', 'ROUGE-SUX']
    
    header = ['week', 'R2', 'R-SU4', 'R2', 'R-SU4', 'R2', 'R-SU4']
    
    body = []
    for sheet in sheets:
        week = sheet + 1
        path = datadir + str(week)+ '/'
        fio.newPath(path)
        
        row = []
        row.append(week)
        for type in types:
            for scorename in scores:
                filename = path + type + "_OUT_"+scorename+".csv"
                lines = fio.readfile(filename)
                try:
                    scorevalues = lines[1].split(',')
                    score = scorevalues[3].strip()
                    row.append(score)
                except Exception:
                    print filename, scorename, lines
        body.append(row)
    fio.writeMatrix(output, body, header)
           
def getWordCount(summary, output):
    head, body = fio.readMatrix(summary, True)
    
    data = []
    
    for row in body:
        newrow = []
        for i in range(len(head)):
            if i==0: continue
            newrow.append( len(row[i].split()) )
        
        data.append(newrow)
    
    newhead = []
    for i in range(len(head)):
        if i==0: continue
        newhead.append("WC_"+head[i])
    
    fio.writeMatrix(output, data, newhead)
    
def getTAWordCountDistribution(excelfile, output):
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    sheets = range(0,12)
    
    datahead = ['Week', '# of sentence POI', '# of sentence POI', '# of sentence POI']
    
    counts = {'POI':{}, 'MP':{}, 'LP':{}}
    for sheet in sheets:
        row = []
        week = sheet + 1
        
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            summaryList = getTASummary(orig, header, summarykey, type)
            for summary in summaryList:
                counts[type][summary]  = len(summary.split())
    
    for type in ['POI', 'MP', 'LP']:
        fio.PrintList(counts[type].values(), sep='\t')
        #fio.PrintDict(counts[type], True)
        #print

def getMeadAverageWordCount(summary, output):
    counts = {'POI':{}, 'MP':{}, 'LP':{}}
    
    for type in ['POI', 'MP', 'LP']:
        summaries = getMeadSummary(datadir, type)
        for weeksummary in summaries:
            for summary in weeksummary:
                counts[type][summary]=len(summary.split())
    
    for type in ['POI', 'MP', 'LP']:
        fio.PrintList(counts[type].values(), sep='\t')

def WriteStudentResponseAverageWords(excelfile, output):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    sheets = range(0,12)
    
    body = []
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        counts = {'POI':{}, 'MP':{}, 'LP':{}}
        
        row = []
        row.append(week)
        
        for type in ['POI', 'MP', 'LP']:
            summary = getStudentSummary(orig, header, summarykey, type=type)
            for s in summary.values():
                counts[type][s] = len(s.split())
        
            row.append(np.mean(counts[type].values()))
            row.append(np.std(counts[type].values()))
        body.append(row)
            
    fio.writeMatrix(output, body, ['Week', 'POI', '', 'MP', '', 'LP', '']) 

def WriteStudentResponseWordCountDistribution(excelfile, output):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    sheets = range(0,25)
    
    counts = {'POI':{}, 'MP':{}, 'LP':{}}
    
    body = []
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        row = []
        for type in ['POI', 'MP', 'LP']:
            summary = getStudentSummary(orig, header, summarykey, type=type)
            for s in summary.values():
                counts[type][s] = len(s.split())
            
    for type in ['POI', 'MP', 'LP']:
    #for type in ['LP']:
        print np.max(counts[type].values()),'\t',np.min(counts[type].values()),'\t',np.mean(counts[type].values()),'\t',np.std(counts[type].values())
        #fio.PrintList(counts[type].values(), sep=',')
        #fio.PrintDict(counts[type], True)
        #print
          
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    output = "../data/2011Spring_overivew.txt"
    summaryoutput = "../data/2011Spring_summary.txt"
    
    datadir = "../../mead/data/2011Spring/"
    datadir_multiple = "../../mead/data/2011SpringMutiple/"
    
    #formatedsummary = '../data/2011Spring_Mead_multiplesummary.txt'
    formatedsummary = '../data/2011Spring_Mead_summary.txt'
    TAwordcount = '../data/2011Spring_ta_wordcount.txt'
    
    rougescore = "../data/2011Spring_rouge_single.txt"
    rougescore_multiple = "../data/2011Spring_rouge_multiple.txt"
    
    #load(excelfile, output)
    #getSummaryOverview(excelfile, summaryoutput)
    
    #Write2Mead(excelfile, datadir)
    #formatSummaryOutput(excelfile, datadir_multiple, output=formatedsummary)
    #formatSummaryOutput(excelfile, datadir, output=formatedsummary)
    #getTAWordCountDistribution(excelfile, TAwordcount)
    #getWordCount(formatedsummary, TAwordcount)
    #getMeadAverageWordCount(formatedsummary, '../data/2011Spring_mead_avaregewordcount.txt')
    #WriteStudentResponseAverageWords(excelfile, '../data/averageword.txt')
    #WriteStudentResponseWordCountDistribution(excelfile, '../data/studentword_distribution.txt')
    #GetRougeScore(datadir_multiple, rougescore_multiple)
    GetRougeScore(datadir, rougescore)
    