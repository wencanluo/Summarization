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

import tfidf
import shallowSummary
import phraseClusteringKmedoid

stopwordfilename = "../../ROUGE-1.5.5/data/smart_common_words.txt"
stopwords = [line.lower().strip() for line in fio.readfile("../../ROUGE-1.5.5/data/smart_common_words.txt")]
print "stopwords:", len(stopwords)

stopwords = stopwords + ['.', '?', '-', ',', '[', ']', '-', ';', '\'', '"', '+', '&', '!', '/', '>', '<', ')', '(', '#', '=']
                    
def Write4Opinosis(student_summaryList, sennafile, output):
    sentences = SennaParser.SennaParse(sennafile)
    
    inputs = []
    for s in sentences:
        wordpos = s.getWordPos(tolower=True)
        
        if not wordpos.endswith("./."):
            wordpos = wordpos + " ./."
        #wordpos = "<s>/. " + wordpos + " </s>/." #add a start and end point
            
        inputs.append(wordpos)
        
    fio.savelist(inputs, output, "\r\n")
                                        
def getShallowSummary(excelfile, folder, sennadatadir, tfidfdir, np, method, K=30):
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

            sennafile = sennadatadir + "senna." + str(week) + "." + type + '.output'
            
            filename = folder + str(week) + '_' + type + '.parsed'
            Write4Opinosis(student_summaryList, sennafile, filename)
                        
def ShallowSummary(excelfile, datadir, sennadatadir, tfidfdir, np, method, K=30):
    getShallowSummary(excelfile, datadir, sennadatadir, tfidfdir, np, method,  K)
    #WriteTASummary(excelfile, datadir)

def WriteSummary(excelfile, folder, datadirOpinosis):
    WriteTASummary(excelfile, folder)
    
    sheets = range(0,12)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        for type in ['POI', 'MP', 'LP']:
            filename = datadirOpinosis + "output/summary/" + str(week) + '_' + type + '.summary.system'
            
            Summary = fio.readfile(filename)
            Summary = [line.strip() for line in Summary]
            
            newS = []
            for s in Summary:
                if s.endswith(' .'):
                    s = s[:-2]
                newS.append(s) 
            Summary = newS
            
            path = folder + str(week)+ '/'
            fio.newPath(path)
            filename = path + type + '.summary'
            
            fio.savelist(Summary, filename)
            
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    
    sennadatadir = "../data/senna/"

    datadirOpinosis = "../../OpinosisSummarizer-1.0/response/"
    #Step 1:
    #ShallowSummary(excelfile, datadirOpinosis + "input/", sennadatadir, tfidfdir=None, np=None, method="Opinosis", K=4)
    
    datadir = "../../mead/data/Opinosis/"
    #Step 2:
    WriteSummary(excelfile, datadir, datadirOpinosis)
          
    print "done"
    