from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET
import numpy as np
from collections import defaultdict
import NLTKWrapper
import SennaParser

from Survey import *
import jsdText
import util

def getKeyPhrase(student_summaryList, sennafile, save2file=None):
    dict = defaultdict(float)
    dict2 = {}
    
    #read senna file
    sentences = SennaParser.SennaParse(sennafile)
    
    #get POS
    for s in sentences:
        words, tags = s.getPrases()
        
        #wordNgrams, tagNgrams = NLTKWrapper.getNgramTokened(words, 3, tags)
        wordNgrams = [" ".join(words)]
        tagNgrams = [" ".join(tags)]
        
        for i, tag in enumerate(tagNgrams):
            dict[tag] = dict[tag] + 1
            dict2[tag] = wordNgrams[i]
    
    if save2file != None:
        fio.SaveDict(dict, save2file, SortbyValueflag = True)
        fio.SaveDict(dict2, save2file + '.word', SortbyValueflag = False)
        
    return dict

def getKeyPOS(student_summaryList, sennafile, save2file=None):
    dict = defaultdict(float)
    dict2 = {}
    
    #read senna file
    sentences = SennaParser.SennaParse(sennafile)
    
    #get POS
    for s in sentences:
        postags = s.getPos()
        wordtags = s.getWords()
        posNgram = NLTKWrapper.getNgram(postags, 1, False)
        wordNgram = NLTKWrapper.getNgram(wordtags, 1, False)
        
        for i, pos in enumerate(posNgram):
            dict[pos] = dict[pos] + 1
            
            if len(posNgram) == len(wordNgram):
                dict2[pos] = wordNgram[i]
    
    if save2file != None:
        fio.SaveDict(dict, save2file, SortbyValueflag = True)
        fio.SaveDict(dict2, save2file + '.word', SortbyValueflag = False)
        
    return dict
            
def getPOS(summaryList, sennafile, save2file=None):
    return getKeyPOS(summaryList, sennafile, save2file=save2file)

def getPhrase(summaryList, sennafile, save2file=None):
    return getKeyPhrase(summaryList, sennafile, save2file=save2file)
                     
def getTASyntax(excelfile, sennadir, outputdir, syntax='pos'):
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
            sennafile = sennadir + 'senna.' + str(week) + '.ta.'+type+'.output'
            
            path = outputdir
            fio.newPath(path)
            
            filename = path + '/ta.' + str(week) +'.' + type + "." + syntax
            
            if syntax == 'pos':
                getPOS(summaryList, sennafile, save2file=filename + ".keys")
            elif syntax == 'phrase':
                getPhrase(summaryList, sennafile, save2file=filename + ".keys")   
            
def getTASyntaxDistribution(sennadir, output, syntax = 'pos'):
    sheets = range(0,12)
    
    dicts = {}
    
    worddict = {}
    
    totaldict = defaultdict(float)
    for type in ['POI', 'MP', 'LP']:
        dict = {}
        for sheet in sheets:
            week = sheet + 1
            filename = sennadir + '/ta.' + str(week) +'.' + type + "." + syntax +".keys"
            wordfile = sennadir + '/ta.' + str(week) +'.' + type + "." + syntax +".keys.word"
            wdict = fio.LoadDict(wordfile)
            worddict = util.UnionDict(worddict, wdict)
            
            tmp = fio.LoadDict(filename, 'float')
            dict = util.UnionDict(dict, tmp)
            
            for k,v in tmp.items():
                totaldict[k] = totaldict[k] + v
        
        dicts[type] = dict
    
    #fio.SaveDict(worddict, output + ".word")
    
    keys = sorted(totaldict, key=totaldict.get, reverse=True)
    
    header = [syntax, 'POI', 'MP', 'LP', 'example']
    body = []
    for key in keys:
        row = []
        row.append(key)
        
        for type in ['POI', 'MP', 'LP']:
            if key in dicts[type]:
                row.append(dicts[type][key])
            else:
                row.append(0)
        
        row.append(worddict[key])
        
        body.append(row)
    
    fio.writeMatrix(output, body, header)

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
    #getTATextForSenna(excelfile, sennadir)
    getTASyntax(excelfile, sennadir, sennadir, 'phrase')
    getTASyntaxDistribution(sennadir, '../data/ta_phrase_distribution.txt', 'phrase')
    print "done"