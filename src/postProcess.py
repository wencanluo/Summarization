from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET

from Survey import *
                    
def formatSummaryOutput(excelfile, datadir, output):
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    sheets = range(0,11)
    
    datahead = ['Week', '# of sentence POI', '# of sentence POI', '# of sentence POI']
    
    head = ['Week', 'TA:POI', 'TA:MP','TA:LP', 'S:POI', 'S:MP','S:LP',]
    body = []
    
    for sheet in sheets:
        row = []
        week = sheet + 1
        row.append(week)
        
        orig = prData(excelfile, sheet)
        summary = getTASummary(orig, header, summarykey)
        if summary == None:
            row.append("")
            row.append("")
            row.append("")
        else:
            for sum in summary:
                if len(sum) != 0:
                    sum = sum.replace("\r", ";")
                    sum = sum.replace("\n", ";")
                #print week, len(sum), sum
                row.append(sum)
                
        for type in ['POI', 'MP', 'LP']:
            path = datadir + str(week)+ '/'
            filename = path + type + '.summary'
            
            lines = fio.readfile(filename)
            sum = " ".join(lines)
            sum = sum.replace("\r", ";")
            sum = sum.replace("\n", ";")
            row.append(sum)
            #print week, len(sum), sum
        
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

def getMeadAverageWordCount(summary, output):
    head, body = fio.readMatrix(summary, True)
    
    data = []
    
    for row in body:
        newrow = []
        for i in range(len(head)):
            if i<=3: continue
            newrow.append( len(row[i].split())/3 )
        
        data.append(newrow)
    
    newhead = []
    for i in range(len(head)):
        if i<=3: continue
        newhead.append(head[i])
    
    fio.writeMatrix(output, data, newhead)

def WriteStudentResponseAverageWords(excelfile, output):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    sheets = range(0,25)
    
    body = []
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        row = []
        for type in ['POI', 'MP', 'LP']:
            summary = getStudentSummary(orig, header, summarykey, type=type)
            
            count = 0
            
            for s in summary.values():
                count = count + len(s.split())
            
            count = count / len(summary)
            row.append(count)
        body.append(row)
    
    fio.writeMatrix(output, body, ['POI', 'MP', 'LP'])        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    output = "../data/2011Spring_overivew.txt"
    summaryoutput = "../data/2011Spring_summary.txt"
    
    datadir = "../../mead/data/2011Spring/"
    datadir_multiple = "../../mead/data/2011SpringMutiple/"
    
    formatedsummary = '../data/2011Spring_Mead_multiplesummary.txt'
    wordcount = '../data/2011Spring_mead_avaregewordcount.txt'
    
    rougescore = "../data/2011Spring_rouge_single.txt"
    rougescore_multiple = "../data/2011Spring_rouge_multiple.txt"
    
    #load(excelfile, output)
    #getSummaryOverview(excelfile, summaryoutput)
    
    #Write2Mead(excelfile, datadir)
    formatSummaryOutput(excelfile, datadir_multiple, output=formatedsummary)
    #getWordCount(formatedsummary, wordcount)
    #getMeadAverageWordCount(formatedsummary, wordcount)
    #WriteStudentResponseAverageWords(excelfile, '../data/averageword.txt')
    #GetRougeScore(datadir_multiple, rougescore_multiple)
    