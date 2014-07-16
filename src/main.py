from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET

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

def getStudentSummaryNum(orig, header, summarykey):
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

def WriteDocsent(excelfile, folder):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    sheets = range(0,25)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            summary = getStudentSummary(orig, header, summarykey, type=type)
            DID = str(week) + '_' + type
            
            path = folder + str(week)+ '/'
            fio.newPath(path)
            path = path + type + '/'
            fio.newPath(path)
            path = path + 'docsent/'
            fio.newPath(path)
            filename = path + DID + '.docsent'
            
            #create a XML file
            root = ET.Element(tag='DOCSENT', attrib = {'DID':DID, 'LANG':"ENG"})
            root.tail = '\n'
            tree = ET.ElementTree(root)
            
            for SNO, value in enumerate(summary.values()):
                node = ET.Element(tag='S', attrib={'PAR':'1', 'RSNT':str(SNO), 'SNO':str(SNO)})
                node.text = value
                node.tail = '\n'
                root.append(node)
            
            tree.write(filename)

def WriteCluster(excelfile, folder):
    sheets = range(0,25)
    
    for type in ['POI', 'MP', 'LP']:
        for sheet in sheets:
            week = sheet + 1
            path = folder + str(week)+ '/'
            fio.newPath(path)
            
            path = path + type + '/'
            fio.newPath(path)
            filename = path + type + '.cluster'
            
            #create a XML file
            root = ET.Element(tag='CLUSTER', attrib = {'LANG':"ENG"})
            root.tail = '\n'
            tree = ET.ElementTree(root)
        
            DID = str(sheet+1) + '_' + type
            
            node = ET.Element(tag='D', attrib={'DID':str(DID)})
            node.tail = '\n'
            root.append(node)
        
            tree.write(filename)
            
def Write2Mead(excelfile, datadir):
    #assume one week is a one document
    #WriteDocsent(excelfile, datadir)
    WriteCluster(excelfile, datadir)

def formatSummaryOutput(excelfile, datadir, output):
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    sheets = range(0,25)
    
    datahead = ['Week', '# of sentence POI', '# of sentence POI', '# of sentence POI']
    
    head = ['Week', 'TA:POI', 'TA:MP','TA:LP', 'S:POI', 'S:MP','S:LP',]
    body = []
    
    for sheet in sheets:
        row = []
        week = sheet + 1
        row.append(week)
        
        orig = prData(excelfile, sheet)
        summary = getTASummary(orig, header, summarykey)
        if summary == None:
            row.append("")
            row.append("")
            row.append("")
        else:
            for sum in summary:
                if len(sum) != 0:
                    sum = sum.replace("\r", ";")
                    sum = sum.replace("\n", ";")
                #print week, len(sum), sum
                row.append(sum)
                
        for type in ['POI', 'MP', 'LP']:
            path = datadir + str(week)+ '/'
            filename = path + type + '.summary'
            
            lines = fio.readfile(filename)
            sum = " ".join(lines)
            sum = sum.replace("\r", ";")
            sum = sum.replace("\n", ";")
            row.append(sum)
            #print week, len(sum), sum
        
        body.append(row)
            
    fio.writeMatrix(output, body, head)

def getWordCount(summary, output):
    head, body = fio.readMatrix(summary, True)
    
    data = []
    
    for row in body:
        newrow = []
        for i in range(len(head)):
            if i==0: continue
            newrow.append( len(row[i].split()) )
        
        data.append(newrow)
    
    newhead = []
    for i in range(len(head)):
        if i==0: continue
        newhead.append("WC_"+head[i])
    
    fio.writeMatrix(output, data, newhead)
    
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    output = "../data/2011Spring_overivew.txt"
    summaryoutput = "../data/2011Spring_summary.txt"
    
    datadir = "../../mead/data/2011Spring/"
    
    formatedsummary = '../../mead/data/2011Spring/2011Spring.txt'
    wordcount = '../../mead/data/2011Spring/2011Spring_wordcount.txt'
    
    #load(excelfile, output)
    #getSummaryOverview(excelfile, summaryoutput)
    
    #Write2Mead(excelfile, datadir)
    #formatSummaryOutput(excelfile, datadir, output=formatedsummary)
    getWordCount(formatedsummary, wordcount)