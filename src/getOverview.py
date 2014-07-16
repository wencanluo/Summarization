from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET

from Survey import *
                    
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
        row.append(getStudentSummaryNum(orig, header, summarykey, type='POI'))
        row.append(getStudentSummaryNum(orig, header, summarykey, type='MP'))
        row.append(getStudentSummaryNum(orig, header, summarykey, type="LP"))
        
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
            summary = getTASummary(orig, header, summarykey)
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
    
    datadir = "../../mead/data/2011Spring/"
    
    #load(excelfile, output)
    #getSummaryOverview(excelfile, summaryoutput)
    