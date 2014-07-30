from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET

from Survey import *
from singledocumentsummarization import WriteTASummary

def WriteDocsent(excelfile, folder):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    sheets = range(0,25)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            summaries = getStudentResponse(orig, header, summarykey, type=type)
            DID = str(week) + '_' + type
            
            path = folder + str(week)+ '/'
            fio.newPath(path)
            path = path + type + '/'
            fio.newPath(path)
            path = path + 'docsent/'
            fio.newPath(path)
            
            for k, v in summaries.items():
                #create a XML file
                root = ET.Element(tag='DOCSENT', attrib = {'DID':DID+'_'+str(k), 'LANG':"ENG"})
                root.tail = '\n'
                tree = ET.ElementTree(root)
                filename = path + DID+'_'+str(k) + '.docsent'
                    
                for RSNT, value in enumerate(v):
                    node = ET.Element(tag='S', attrib={'PAR':'1', 'RSNT': str(RSNT+1), 'SNO':str(RSNT+1)})
                    node.text = value
                    node.tail = '\n'
                    root.append(node)
                
                tree.write(filename)
            
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
            summaries = getStudentResponse(orig, header, summarykey, type)
            
            for k, v in summaries.items():
                node = ET.Element(tag='D', attrib={'DID':DID+'_'+str(k)})
                node.tail = '\n'
                root.append(node)
        
            tree.write(filename)
            
def Write2Mead(excelfile, datadir):
    #assume one student's response is a one document
    WriteDocsent(excelfile, datadir)
    WriteCluster(excelfile, datadir)
    WriteTASummary(excelfile, datadir)
        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    datadir = "../../mead/data/2011SpringMutiple/"
    
    fio.deleteFolder(datadir)
    Write2Mead(excelfile, datadir)
    