from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET

import CourseMirrorSurvey

course = "CS2001"
#course = "CS2610"
maxWeekDict = {"CS2610": 21, 
               "CS2001": 18}

maxWeek = maxWeekDict[course]
                    
def WriteDocsent(excelfile, folder):
    sheets = range(0,maxWeek)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        for type in ['POI', 'MP', 'LP']:
            summaries = CourseMirrorSurvey.getStudentResponse(excelfile, course, week, type=type)
            if len(summaries) == 0: continue
            
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
            
            sno_id = 1
            for par, summaryList in enumerate(summaries.values()):
                for RSNT, value in enumerate(summaryList):
                    node = ET.Element(tag='S', attrib={'PAR':str(par+1), 'RSNT':str(RSNT+1), 'SNO':str(sno_id)})
                    node.text = value
                    node.tail = '\n'
                    root.append(node)
                    sno_id = sno_id + 1
            
            tree.write(filename)
            print filename
            
def WriteCluster(excelfile, folder):
    sheets = range(0,maxWeek)
    
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
            
def Write2Mead(excelfile, datadir, K=3):
    #assume one week is a one document
    WriteDocsent(excelfile, datadir)
    WriteCluster(excelfile, datadir)
    #WriteTASummary(excelfile, datadir)
   
if __name__ == '__main__':    
    for c in ["CS2001", "CS2610"]:
        course = c
        maxWeek = maxWeekDict[course]
        
        excelfile = "../data/reflections.json"
        datadir = "../../mead/data/"+course+"_Mead/"
        fio.deleteFolder(datadir)
        Write2Mead(excelfile, datadir)
        
    print "done"
    