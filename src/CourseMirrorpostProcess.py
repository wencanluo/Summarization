from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET
import numpy as np
from collections import defaultdict
import NLTKWrapper

import CourseMirrorSurvey
import Survey

course = "CS2610"

maxWeek = maxWeekDict[course]
                    
def formatSummaryOutput(datadir, models, output):
    sheets = range(0,maxWeek)
    
    head = ['Week',]
    
    for type in ['POI', 'MP', 'LP']:
        head = head + ['A', 'B', 'C', 'D']
        
    body = []
    
    for sheet in sheets:
        row = []
        week = sheet + 1
        row.append(CourseMirrorSurvey.WeekLecture[course][week-1])
        for type in ['POI', 'MP', 'LP']:
            for model in models:
                summaries = Survey.getMeadSummary(datadir + course +'_'+ model+'/', type)
                                
                summary = ";".join(summaries[sheet])
                row.append(summary)
        
        body.append(row)
            
    fio.writeMatrix(output, body)

       
if __name__ == '__main__':
    
    output = "../data/"+course+"CourseMirror_summary.txt" 
    datadir = "../../mead/data/"
    formatSummaryOutput(datadir, ['ShallowSummary_unigram', 'ShallowSummary_NPhraseSoft', 'Mead', 'ShallowbasedExtrativeSummary_unigram'], output)
    
    print "done"