from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET

from Survey import *
import random
                    
def getRandomSummary(excelfile, folder, K=3):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    sheets = range(0,12)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            student_summaries = getStudentResponse(orig, header, summarykey, type)
            student_summaryList = []
            
            for summaryList in student_summaries.values():
                for s in summaryList:
                    student_summaryList.append(s)
                    
            DID = str(week) + '_' + type
            
            path = folder + str(week)+ '/'
            fio.newPath(path)
            filename = path + type + '.summary'
            
            randomSummary = []
            ranges = range(len(student_summaryList))
            random.shuffle(ranges)
            
            for i in range(K):
                randomSummary.append("[" + str(i+1) + "]  " + student_summaryList[ranges[i]])
            
            fio.savelist(randomSummary, filename)
            
def getLongestSummary(excelfile, folder, K=3):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    sheets = range(0,12)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            student_summaries = getStudentResponse(orig, header, summarykey, type)
            student_summaryDict = {}
            
            for summaryList in student_summaries.values():
                for s in summaryList:
                    student_summaryDict[s] = len(s.split())
                    
            DID = str(week) + '_' + type
            
            path = folder + str(week)+ '/'
            fio.newPath(path)
            filename = path + type + '.summary'
            
            student_summaryList = sorted(student_summaryDict, key=student_summaryDict.get, reverse = True)
            longestSummary = []
            for i in range(K):
                longestSummary.append("[" + str(i+1) + "]  " + student_summaryList[i])
            
            fio.savelist(longestSummary, filename)

def getShortestSummary(excelfile, folder, K=3):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    sheets = range(0,12)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            student_summaries = getStudentResponse(orig, header, summarykey, type)
            student_summaryDict = {}
            
            for summaryList in student_summaries.values():
                for s in summaryList:
                    student_summaryDict[s] = len(s.split())
                    
            DID = str(week) + '_' + type
            
            path = folder + str(week)+ '/'
            fio.newPath(path)
            filename = path + type + '.summary'
            
            student_summaryList = sorted(student_summaryDict, key=student_summaryDict.get)
            longestSummary = []
            for i in range(K):
                longestSummary.append("[" + str(i+1) + "]  " + student_summaryList[i])
            
            fio.savelist(longestSummary, filename)
                        
def WriteTASummary(excelfile, datadir):
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    summarykey = "Top Answers"
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    sheets = range(0,12)
    types = ['POI', 'MP', 'LP']
    
    for sheet in sheets:
        week = sheet + 1
        path = datadir + str(week)+ '/'
        fio.newPath(path)

        orig = prData(excelfile, sheet)
        for type in types:
            summary = getTASummary(orig, header, summarykey, type)
            
            filename = path + type + '.ref.summary'
            print filename
            
            #only save the first 3 points
            fio.savelist(summary, filename)

def RandomSummary(excelfile, datadir, K=3):
    getRandomSummary(excelfile, datadir, K)
    WriteTASummary(excelfile, datadir)

def LongestSummary(excelfile, datadir, K=3):
    getLongestSummary(excelfile, datadir, K)
    WriteTASummary(excelfile, datadir)
    
def ShortestSummary(excelfile, datadir, K=3):
    getShortestSummary(excelfile, datadir, K)
    WriteTASummary(excelfile, datadir)
       
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    
    datadir = "../../mead/data/RandombaselineK3/"
    fio.deleteFolder(datadir)
    RandomSummary(excelfile, datadir, K=3)
    
    datadir = "../../mead/data/RandombaselineK2/"
    fio.deleteFolder(datadir)
    RandomSummary(excelfile, datadir, K=2)
    
    datadir = "../../mead/data/RandombaselineK1/"
    fio.deleteFolder(datadir)
    RandomSummary(excelfile, datadir, K=1)
    
    datadir = "../../mead/data/LongestbaselineK3/"
    fio.deleteFolder(datadir)
    LongestSummary(excelfile, datadir, K=3)
    
    datadir = "../../mead/data/LongestbaselineK2/"
    fio.deleteFolder(datadir)
    LongestSummary(excelfile, datadir, K=2)
    
    datadir = "../../mead/data/LongestbaselineK1/"
    fio.deleteFolder(datadir)
    LongestSummary(excelfile, datadir, K=1)
    
    datadir = "../../mead/data/ShortestbaselineK3/"
    fio.deleteFolder(datadir)
    ShortestSummary(excelfile, datadir, K=3)
    
    datadir = "../../mead/data/ShortestbaselineK2/"
    fio.deleteFolder(datadir)
    ShortestSummary(excelfile, datadir, K=2)
    
    datadir = "../../mead/data/ShortestbaselineK1/"
    fio.deleteFolder(datadir)
    ShortestSummary(excelfile, datadir, K=1)
    
    