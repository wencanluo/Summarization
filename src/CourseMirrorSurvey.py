from OrigReader import prData
import sys
import re
import fio
import NLTKWrapper
import json

#filters = ["?", "[blank]", 'n/a', 'blank', 'none', "no", "nothing"]
filters = []

#header = ['Timestamp', 'cid', 'lecture_number', 'user', 'q1', 'q2', 'q3']
header = ['Timestamp', 'cid', 'lecture_number', 'user', 'q1', 'q2']

maxWeekDict = {"CS2610": 21-4+1, 
               "CS2001": 18-5+1,
               "PHYS0175":13,
               "IE256":2,
               }

WeekLecture = {"CS2610":range(4, 40),
               "CS2001":range(5, 40),
               "PHYS0175": range(5, 24),
               "IE256": range(1,3),
               }

import datetime

RatingKey = {"slightly": 1, 
"somewhat": 2,
"moderately": 3, 
"mostly":4,
"completely":5
}

RateSplitTag = "||Rating: "

def getRatingkey(rate):
    key = rate.strip().lower()
    if key in RatingKey:
        return RatingKey[key]
    return -1

def NormalizeResponse(response):
    k = response.find(RateSplitTag)
    if k == -1:
        return response
    return response[:k]

def ExtractTimeStamp(excelfile, output):
    header = ['Timestamp', 'user', 'q1', 'q2', 'q3']    
    orig = prData(excelfile, 0)
    
    data = []
    for inst in orig._data:
        dict = {}
        for h in header:
            if h == "Timestamp":
                seconds = (inst[h] - 25569) * 86400.0
                t = datetime.datetime.utcfromtimestamp(seconds)
                #dict[h] = str(t)
                dict[h] = seconds
            else:
                dict[h] = inst[h]
        
        data.append(dict)
        
    f = open(output,'w')
    json.dump(data,f,indent=2)
    f.close()
                        
def HasSummary(orig, header, summarykey):
    key = header[0]
    for k, inst in enumerate(orig._data):
        try:
            value = inst[key].lower().strip()
            if value == summarykey.lower():
                if len(inst[header[2]].strip()) > 0:
                    return True
        except Exception:
            return False
    return False

def NormalizedTASummary(summary):
    summary = summary.strip()
    g = re.search('^\d+\)(.*)\[\d+\]$', summary)
    if g != None:
        summary = g.group(1).strip()
    
    g = re.search('^(.*)\[\d+\]$', summary)
    if g != None:
        summary = g.group(1).strip()
    
    g = re.search('^\d+\)(.*)$', summary)
    if g != None:
        summary = g.group(1).strip()
    
    return summary.strip()

def NormalizeMeadSummary(summary):
    summary = summary.strip()
    g = re.search('^\[\d+\](.*)$', summary)
    if g != None:
        summary = g.group(1).strip()
    
    return summary.strip()
            
def getStudentResponse(excelfile, course, week, type='POI'):
    '''
    return a dictionary of the students' summary, with the student id as a key
    The value is a list with each sentence an entry
    '''
    f = open(excelfile)
    reflections = json.load(f)['results']
    f.close()
    
    tokenIndex = 'user'
    couseIndex = 'cid'
    lectureIndex = 'lecture_number'
    
    summaries = {}
    
    if type=='POI':
        key = 'q1'
    elif type=='MP':
        key = 'q2'
    elif type=='LP':
        key = 'q3'
    else:
        return None
    
     #a classifier to predict whether the student has problem
    #filters = []
    week = week-1
    
    for k, inst in enumerate(reflections):
        try:
            token = inst[tokenIndex].lower().strip()
            courseNow = inst[couseIndex].strip()
            lecture = inst[lectureIndex]
            
            if courseNow != course: continue
            if WeekLecture[course][week] != lecture: continue
            
            if len(token) > 0:
                content = inst[key].strip()
                if content.lower() in filters: continue
                if len(content) > 0:                    
                    summary = NLTKWrapper.splitSentence(content)
                    summaries[token] = summary
            else:
                break
        except Exception:
            return summaries
    return summaries

def getStudentResponseList(excelfile, course, week, type='POI', withSource=False):
    student_summaries = getStudentResponse(excelfile, course, week, type)
    student_summaryList = []
    
    for id, summaryList in student_summaries.items():
        for s in summaryList:
            s = NormalizeResponse(s)
            student_summaryList.append((s,id))
            
    if withSource:
        return student_summaryList
    else:
        return [summary[0] for summary in student_summaryList]
                        
def getStudentSummaryNum(orig, header, summarykey, type='POI'):
    if type=='POI':
        key = header[2]
    elif type=='MP':
        key = header[3]
    elif type=='LP':
        key = header[4]
    else:
        return 0
    
    count = 0
    for k, inst in enumerate(orig._data):
        try:
            value = inst['ID'].lower().strip()
            if len(value) > 0:
                if len(inst[key].lower().strip()) > 0:
                    count = count + 1
            else:
                break
        except Exception:
            return 0
    return count-1

def getMaleNum(orig, header, summarykey):
    key = header[1]
    count = 0
    for k, inst in enumerate(orig._data):
        try:
            value = inst[key].lower().strip()
            if value == 'm':
                count = count + 1
        except Exception:
            return 0
    return count

def getStudentNum(orig, header, summarykey):
    key = header[0]
    count = 0
    for k, inst in enumerate(orig._data):
        try:
            value = inst[key].lower().strip()
            if len(value) > 0:
                count = count + 1
            else:
                break
        except Exception:
            return 0
    return count-1

def getMeadSummary(datadir, type):
    #return a list of summaries, week by week. The summary for each week is also a list
    sheets = range(0,12)
    
    summaries = []
    
    for sheet in sheets:
        row = []
        week = sheet + 1
        row.append(week)
                    
        path = datadir + str(week)+ '/'
        filename = path + type + '.summary'
        
        lines = fio.ReadFile(filename)
        summary = []
        for line in lines:
            summary.append(NormalizeMeadSummary(line))
        
        summaries.append(summary)
    
    return summaries
        
def getMeadSummaryList(datadir, type):
    #return a list of summaries, week by week. The summary for each week is also a list
    sheets = range(0,12)
    
    summaries = []
    for sheet in sheets:
        row = []
        week = sheet + 1
        row.append(week)
                    
        path = datadir + str(week)+ '/'
        filename = path + type + '.summary'
        
        lines = fio.ReadFile(filename)
        summary = []
        for line in lines:
            summary.append(NormalizeMeadSummary(line))
        
        summaries.append(summary)
    
    summaryList = []
    for summaries in summaries:
        for summary in summaries:
            summaryList.append(summary)
        
    return summaryList

def getStudentResponses4Senna(excelfile, datadir):
    sheets = range(0, maxWeek)
    
    for i, sheet in enumerate(sheets):
        week = i + 1

        for type in ['POI', 'MP', 'LP']:
            student_summaryList = getStudentResponseList(excelfile, course, week, type)
            if len(student_summaryList) == 0: continue
            
            filename = datadir + "senna." + str(week) + "." + type + ".input"
            
            fio.SaveList(student_summaryList, filename)
            
if __name__ == '__main__':
    
    excelfile = "../data/CourseMIRROR Reflections (Responses).xls"
    output = "../data/CourseMIRROR_reflections.json"
    
    #ExtractTimeStamp(excelfile, output)
    
    #Step1: Prepare Senna Input
    for c in ["IE256"]:#PHYS0175
        course = c
        maxWeek = maxWeekDict[course]
         
        sennadir = "../data/"+course+"/senna/"
        excelfile = "../data/CourseMirror/Reflection.json"
        phrasedir = "../data/"+course+"/phrases/"
         
        fio.NewPath(sennadir)
        getStudentResponses4Senna(excelfile, sennadir)


    #Step2: get Senna output
    