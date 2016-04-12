from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET

import phraseClusteringKmedoid

import SennaParser
import CourseMirrorSurvey
from CourseMirrorSurvey import maxWeekDict

import MaximalMatchTokenizer

course = "CS2001"
       
def WriteDocsent(excelfile, folder, sennadatadir, phrasedir, np=None):
    sheets = range(0,maxWeek)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        for type in ['POI', 'MP', 'LP']:
            student_summaryList = CourseMirrorSurvey.getStudentResponseList(excelfile, course, week, type, withSource=True)
            if len(student_summaryList) == 0: continue
            
            ids = [summary[1] for summary in student_summaryList]
            summaries = [summary[0] for summary in student_summaryList] 
                            
            sennafile = sennadatadir + "senna." + str(week) + "." + type + '.output'
            if not fio.IsExist(sennafile): continue
            
            phrasefile = phrasedir + str(week) + ".txt"
            
            sentences = SennaParser.SennaParse(sennafile)
            
            DID = str(week) + '_' + type
            
            path = folder + str(week)+ '/'
            fio.NewPath(path)
            path = path + type + '/'
            fio.NewPath(path)
            path = path + 'docsent/'
            fio.NewPath(path)
            filename = path + DID + '.docsent'
            
            #create a XML file
            root = ET.Element(tag='DOCSENT', attrib = {'DID':DID, 'LANG':"ENG"})
            root.tail = '\n'
            tree = ET.ElementTree(root)
            
            if np.startswith("candidate"):
                summariesList = summaries
            else:
                summariesList = sentences
            
            sno_id = 1
            for par, s in enumerate(summariesList):
                if np== "candidate":
                    NPs = MaximalMatchTokenizer.MaximalMatchTokenizer(s, phrasefile, stemming=False)
                elif np == 'candidatestemming':
                    NPs = MaximalMatchTokenizer.MaximalMatchTokenizer(s, phrasefile)
                elif np=='syntax':
                    NPs = s.getSyntaxNP()
                    NPs = phraseClusteringKmedoid.MalformedNPFlilter(NPs)
                elif np == 'chunk':
                    NPs = s.getNPrases()
                    NPs = phraseClusteringKmedoid.MalformedNPFlilter(NPs)
                elif np == 'sentence':
                    NPs = s.getSentence()
                else:
                    print "wrong"
                    exit()
                    
                for RSNT, value in enumerate(NPs):
                    node = ET.Element(tag='S', attrib={'PAR':str(par+1), 'RSNT':str(RSNT+1), 'SNO':str(sno_id)})
                    node.text = value
                    node.tail = '\n'
                    root.append(node)
                    sno_id = sno_id + 1
            
            tree.write(filename)
            
def WriteCluster(excelfile, folder, np=None):
    sheets = range(0,maxWeek)
    
    for type in ['POI', 'MP']:#, 'LP'
        for sheet in sheets:
            week = sheet + 1
            path = folder + str(week)+ '/'
            fio.NewPath(path)
            
            path = path + type + '/'
            fio.NewPath(path)
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
            
def Write2Mead(excelfile, datadir, sennadatadir, phrasedir, np=None):
    #assume one week is a one document
    WriteDocsent(excelfile, datadir, sennadatadir, phrasedir, np)
    WriteCluster(excelfile, datadir)
                
if __name__ == '__main__':
    
    #Step4: get PhraseMead input
    
    for c in ['IE256']: #["CS2001", "CS2610"]:
        course = c
        maxWeek = maxWeekDict[course]
        
        sennadir = "../data/"+course+"/senna/"
        excelfile = "../data/CourseMirror/Reflection.json"
        phrasedir = "../data/"+course+"/np/"
        
        coursename = 'IE256_C4/'
        for np in ['syntax']:
            datadir = "../../mead/data/"+coursename+"PhraseMead/"
            fio.DeleteFolder(datadir)
            Write2Mead(excelfile, datadir, sennadir, phrasedir, np=np)
 
        for np in ['syntax']:
            datadir = "../../mead/data/"+coursename+"PhraseMeadMMR/"
            fio.DeleteFolder(datadir)
            Write2Mead(excelfile, datadir, sennadir, phrasedir, np=np)
                 
        for np in ['syntax']:
            datadir = "../../mead/data/"+coursename+"PhraseLexRank/"
            fio.DeleteFolder(datadir)
            Write2Mead(excelfile, datadir, sennadir, phrasedir, np=np)
         
        for np in ['syntax']:
            datadir = "../../mead/data/"+coursename+"PhraseLexRankMMR/"
            fio.DeleteFolder(datadir)
            Write2Mead(excelfile, datadir, sennadir, phrasedir, np=np)
                
        for np in ['sentence']:
            datadir = "../../mead/data/"+coursename+"Mead/"
            fio.DeleteFolder(datadir)
            Write2Mead(excelfile, datadir, sennadir, phrasedir, np=np)
            
    #Step5: get PhraseMead output
    
    print "done"