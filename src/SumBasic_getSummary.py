import sys
import re
import fio
from collections import defaultdict
from Survey import *
import random
import NLTKWrapper

import SumBasic_sentence as SumBasic
            
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
            student_summaryList = getStudentResponseList(orig, header, summarykey, type)

            path = folder + str(week)+ '/'
            fio.NewPath(path)
            filename = path + type + '.txt'
            
            fio.SaveList(student_summaryList, filename)
            
            #run the SumBasic
            distribution, clean_sentences, processed_sentences = SumBasic.get_sentences(filename)
            summary = SumBasic.summarize(distribution, clean_sentences, processed_sentences, K)
            
            filename = path + type + '.summary'
            fio.SaveList(summary, filename)
            
                        
def ShallowSummary(excelfile, datadir, K=30):
    getShallowSummary(excelfile, datadir, K)
    WriteTASummary(excelfile, datadir)
        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    
    sennadatadir = "../data/senna/"
    
    for model in ['unigram_remove_stop', 'bigram']:
        datadir = "../../mead/data/C4_SumBasic/"  
        fio.DeleteFolder(datadir)
        ShallowSummary(excelfile, datadir, K=4)

    print 'done'
    