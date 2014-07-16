from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET

from Survey import *

def WriteDocsent(excelfile, folder):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    sheets = range(0,25)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            summaries = getStudentSummary(orig, header, summarykey, type=type)
            DID = str(week) + '_' + type
            
            path = folder + str(week)+ '/'
            fio.newPath(path)
            path = path + type + '/'
            fio.newPath(path)
            path = path + 'docsent/'
            fio.newPath(path)
            

            for k, v in summaries.items():
                filename = path + DID+'_'+str(k) + '.docsent'
                
                #create a XML file
                root = ET.Element(tag='DOCSENT', attrib = {'DID':DID+'_'+str(k), 'LANG':"ENG"})
                root.tail = '\n'
                tree = ET.ElementTree(root)
            
                node = ET.Element(tag='S', attrib={'PAR':'1', 'RSNT':'1', 'SNO':'1'})
                node.text = v
                node.tail = '\n'
                root.append(node)
            
                tree.write(filename)
                #print filename
            

def WriteCluster(excelfile, folder):
    sheets = range(0,25)
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
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
            
            orig = prData(excelfile, sheet)
            summaries = getStudentSummary(orig, header, summarykey, type)
            
            for k, v in summaries.items():
                node = ET.Element(tag='D', attrib={'DID':DID+'_'+str(k)})
                node.tail = '\n'
                root.append(node)
        
            tree.write(filename)
            
def Write2Mead(excelfile, datadir):
    #assume one student's response is a one document
    WriteDocsent(excelfile, datadir)
    #WriteCluster(excelfile, datadir)
    #WriteTASummary(excelfile, datadir)

def WriteTASummary(excelfile, datadir):
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    summarykey = "Top Answers"
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    sheets = range(0,25)
    types = ['POI', 'MP', 'LP']
    
    for sheet in sheets:
        week = sheet + 1
        path = datadir + str(week)+ '/'
        fio.newPath(path)

        orig = prData(excelfile, sheet)
        summaries = getTASummary(orig, header, summarykey)
        if summaries == None: continue
        
        for i in range(len(summaries)):
            summary = summaries[i]
            type = types[i]
            filename = path + type + '.ref.summary'
            print filename
            
            fio.saveText(summary, filename)
        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    datadir = "../../mead/data/2011SpringMutiple/"
    
    Write2Mead(excelfile, datadir)
    