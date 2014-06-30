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

def getSummary(orig, header, summarykey):
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

def getPOISummaryNum(orig, header, summarykey):
    key = header[2]
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

def getMPSummaryNum(orig, header, summarykey):
    key = header[3]
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
 
def getLPSummaryNum(orig, header, summarykey):
    key = header[4]
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
                    
def getOverview(excelfile, output):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    sheets = range(0,25)
    
    datahead = ['Week', 'Has summary', '# of student', '# of Male', '# of POI', '# of MP', '# of LP']
    body = []
    for sheet in sheets:
        orig = prData(excelfile, sheet)
        row = []
        row.append(sheet+1)
        
        row.append(HasSummary(orig, header, summarykey))
        row.append(getStudentNum(orig, header, summarykey))
        row.append(getMaleNum(orig, header, summarykey))
        row.append(getPOISummaryNum(orig, header, summarykey))
        row.append(getMPSummaryNum(orig, header, summarykey))
        row.append(getLPSummaryNum(orig, header, summarykey))
        
        for k, inst in enumerate(orig._data):
            for key in header:
                try:
                    value = inst[key].lower().strip()
                except Exception:
                    print sheet, k, key
        
        body.append(row)

    fio.writeMatrix(output, body, datahead)
    
def getSummaryOverview(excelfile, output):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    sheets = range(0,25)
    
    datahead = ['Week', '# of sentence POI', '# of sentence POI', '# of sentence POI']
    body = []
    for sheet in sheets:
        orig = prData(excelfile, sheet)
        row = []
        row.append(sheet+1)
        
        if not HasSummary(orig, header, summarykey):
            row.append(0)
            row.append(0)
            row.append(0)
        else:
            summary = getSummary(orig, header, summarykey)
            for sum in summary:
                points = sum.split('\n')
                row.append(len(points))
        
        body.append(row)

    fio.writeMatrix(output, body, datahead)
    
def load(excelfile, output):    
    getOverview(excelfile, output)
        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    output = "../data/2011Spring_overivew.txt"
    summaryoutput = "../data/2011Spring_summary.txt"
    
    load(excelfile, output)
    getSummaryOverview(excelfile, summaryoutput)