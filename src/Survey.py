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

def getTASummary(orig, header, summarykey):
    if not HasSummary(orig, header, summarykey):
        return None
    
    keys = ['Point of Interest', 'Muddiest Point', 'Learning Point']
    key = header[0]
    
    summary = []
    for k, inst in enumerate(orig._data):
        value = inst[key].lower().strip()
        if value == summarykey.lower():
            for keyword in keys:
                value = inst[keyword].strip()
                summary.append(value)
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
                content = inst[key].lower().strip()
                if content == 'blank': continue
                
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
        
if __name__ == '__main__':
    pass
    