from OrigReader import prData
import sys
import re
import fio
import NLTKWrapper

header = ['Timestamp', 'Course', 'Lecture', 'Your Token', 'Point of Interest', 'Muddiest Point', 'Learning Point']

WeekLecture = {"CS2610":["Lecture 4", "Lecture 5", "Lecture 6", "Lecture 7", "Lecture 8", "Lecture 9", "Lecture 10",],
               "CS2001": ["Lecture 5"]}
                    
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

def getTASummary(orig, header, summarykey, type='POI'):
    '''
    Get TA's summary from the excel
    return a list of sentences
    '''
    if not HasSummary(orig, header, summarykey):
        return []
    
    if type=='POI':
        keyword = header[2]
    elif type=='MP':
        keyword = header[3]
    elif type=='LP':
        keyword = header[4]
    else:
        return []
    
    key = header[0]
    
    summary = []
    for k, inst in enumerate(orig._data):
        value = inst[key].lower().strip()
        if value == summarykey.lower():
            value = inst[keyword].strip()
            summaries = value.split("\n")
            for sum in summaries:
                summary.append(NormalizedTASummary(sum))
    return summary

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
            
def getStudentResponse(excelfile, course, week, type='POI'):
    '''
    return a dictionary of the students' summary, with the student id as a key
    The value is a list with each sentence an entry
    '''
    orig = prData(excelfile, 0)
    tokenIndex = 'Your Token'
    couseIndex = 'Course'
    lectureIndex = 'Lecture'
    
    summaries = {}
    
    if type=='POI':
        key = 'Point of Interest'
    elif type=='MP':
        key = 'Muddiest Point'
    elif type=='LP':
        key = 'Learning Point'
    else:
        return None
    
    filters = ["?", "[blank]", 'n/a', 'blank', 'none', "None"] #a classifier to predict whether the student has problem
    #filters = []
    week = week-1
    
    for k, inst in enumerate(orig._data):
        try:
            token = inst[tokenIndex].lower().strip()
            courseNow = inst[couseIndex].strip()
            lecture = inst[lectureIndex].strip()
            
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

def getStudentResponseList(excelfile, course, week, type='POI'):
    student_summaries = getStudentResponse(excelfile, course, week, type)
    student_summaryList = []
    
    for summaryList in student_summaries.values():
        for s in summaryList:
            student_summaryList.append(s)
    return student_summaryList
                    
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
        
        lines = fio.readfile(filename)
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
        
        lines = fio.readfile(filename)
        summary = []
        for line in lines:
            summary.append(NormalizeMeadSummary(line))
        
        summaries.append(summary)
    
    summaryList = []
    for summaries in summaries:
        for summary in summaries:
            summaryList.append(summary)
        
    return summaryList
            
if __name__ == '__main__':
    pass
    