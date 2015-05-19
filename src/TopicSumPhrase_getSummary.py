import sys
import re
import fio
from collections import defaultdict
from Survey import *
import random
import NLTKWrapper
import xml.etree.ElementTree as ET

import os
import SumBasic_word as SumBasic

import KLSum_getSummary
import phraseClusteringKmedoid

TOPICSUM_EXE = "../../summarizer/src/run_TopicSum_word.exe"
                     
def getShallowSummary(excelfile, folder, K):
    #K is the number of words per points
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    sheets = range(0,12)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            print excelfile, sheet, type
            student_summaryList = getStudentResponseList(orig, header, summarykey, type, withSource=True)
            
            ids = [summary[1] for summary in student_summaryList]
            summaries = [summary[0] for summary in student_summaryList]
            
            sennafile = sennadatadir + "senna." + str(week) + "." + type + '.output'
            NPCandidates, sources = phraseClusteringKmedoid.getNPs(sennafile, MalformedFlilter=True, source=ids, np='syntax')
            

            path = folder + str(week)+ '/'
            fio.NewPath(path)
            xlm = path + type + '.xml'
            
            filename = path + type + '.txt'
            fio.SaveList(NPCandidates, filename)
            KLSum_getSummary.toXMLDocument(filename, xlm)
            
            summaryfile = path + type + '.summary'
            
            #run the KL
            cmd =  TOPICSUM_EXE + ' ' + xlm + ' ' + summaryfile
            
            print cmd
            os.system(cmd)
            
                        
def ShallowSummary(excelfile, datadir, K=30):
    getShallowSummary(excelfile, datadir, K)
    WriteTASummary(excelfile, datadir)
        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    
    sennadatadir = "../data/senna/"
    
    datadir = "../../mead/data/C30_TopicSumPhrase/"  
    fio.DeleteFolder(datadir)
    ShallowSummary(excelfile, datadir, K=30)

    print 'done'
    