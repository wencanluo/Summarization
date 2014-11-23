from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET

from Survey import *
import phraseClusteringKmedoid

                    
def WriteDocsent(excelfile, folder, sennadatadir, phrasedir, np=None):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    sheets = range(0,12)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            
            student_summaryList = getStudentResponseList(orig, header, summarykey, type, withSource=True)
            
            ids = [summary[1] for summary in student_summaryList]
            summaries = [summary[0] for summary in student_summaryList] 
                            
            sennafile = sennadatadir + "senna." + str(week) + "." + type + '.output'
            phrasefile = phrasedir + str(week) + ".txt"
            
            sentences = SennaParser.SennaParse(sennafile)
            
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
    sheets = range(0,12)
    
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
            
def Write2Mead(excelfile, datadir, sennadatadir, phrasedir, np=None):
    #assume one week is a one document
    WriteDocsent(excelfile, datadir, sennadatadir, phrasedir, np)
    WriteCluster(excelfile, datadir)
    WriteTASummary(excelfile, datadir)
                
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    sennadir = "../data/senna/"
    phrasedir = "../data/phrases/"
    outputdir = "../data/np/"
    for np in ['syntax']:#'candidate', 'candidatestemming']:
        datadir = "../../mead/data/C30_PhraseMead_"+np+"/"
        fio.deleteFolder(datadir)
        Write2Mead(excelfile, datadir, sennadir, phrasedir, np=np)
        
        datadir = "../../mead/data/C30_LexRank_"+np+"/"
        fio.deleteFolder(datadir)
        Write2Mead(excelfile, datadir, sennadir, phrasedir, np=np)
                    
        datadir = "../../mead/data/C30_PhraseMeadMMR_"+np+"/"
        fio.deleteFolder(datadir)
        Write2Mead(excelfile, datadir, sennadir, phrasedir, np=np)
          
        datadir = "../../mead/data/C30_PhraseMeadLexRank_"+np+"/"
        fio.deleteFolder(datadir)
        Write2Mead(excelfile, datadir, sennadir, phrasedir, np=np)
          
        datadir = "../../mead/data/C30_PhraseMeadLexRankMMR_"+np+"/"
        fio.deleteFolder(datadir)
        Write2Mead(excelfile, datadir, sennadir, phrasedir, np=np)
        
        datadir = "../../mead/data/C30_LexRankMMR_"+np+"/"
        fio.deleteFolder(datadir)
        Write2Mead(excelfile, datadir, sennadir, phrasedir, np=np)
    