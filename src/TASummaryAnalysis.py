from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET
import numpy as np
from collections import defaultdict
import NLTKWrapper

from Survey import *
import jsdText

def getTATextForSenna(excelfile, sennadir):
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
            filename = sennadir + 'senna.' + str(week) + '.ta.'+type+'.input'
            fio.savelist(summaryList, filename)
                                    
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
                unigram = NLTKWrapper.getNgram(summary, 1)
                
                for word in unigram:
                    word = word.lower()
                    if word in NLTKWrapper.punctuations: continue
                    if word not in counts[type]:
                        counts[type][word] = 0
                    counts[type][word] = counts[type][word] + 1
                    
    
    for type in ['POI', 'MP', 'LP']:
        filename = output + "_" + type + '.txt'
        fio.SaveDict(counts[type], filename, True)

def getJSD(inputdirpredix, output):
    dicts = {}
    for type in ['POI', 'MP', 'LP']:
        filename = inputdirpredix + "_" + type + '.txt'
        dict = fio.LoadDict(filename, 'float')
        dicts[type] = dict
    
    header = ['','POI', 'MP', 'LP']
    body = []
    for type1 in ['POI', 'MP', 'LP']:
        row = []
        row.append(type1)
        for type2 in ['POI', 'MP', 'LP']:    
            row.append(jsdText.JSDDict(dicts[type1], dicts[type2]))
        
        body.append(row)
    
    fio.writeMatrix(output, body, header)
        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    prefix = '../data/ta_word_distribution'
    sennadir = '../data/senna/'
    
    #getTAWordCountDistribution(excelfile, prefix)
    #getJSD(prefix, "../data/ta_jsd.txt")
    getTATextForSenna(excelfile, sennadir)
    print "done"