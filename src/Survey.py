from OrigReader import prData
import sys
import re
import fio
                    
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

def getStudentSummary(orig, header, summarykey, type='POI'):
    '''
    return a dictionary of the students' summary, with the student id as a key
    '''
    summary = {}
    
    if type=='POI':
        key = header[2]
    elif type=='MP':
        key = header[3]
    elif type=='LP':
        key = header[4]
    else:
        return None
    
    for k, inst in enumerate(orig._data):
        try:
            value = inst['ID'].lower().strip()
            if value == 'top answers': continue
            
            if len(value) > 0:
                content = inst[key].strip()
                if content.lower() == 'blank': continue
                
                if len(content) > 0:
                    summary[value] = content
            else:
                break
        except Exception:
            return summary
    return summary

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
        
            
if __name__ == '__main__':
    pass
    