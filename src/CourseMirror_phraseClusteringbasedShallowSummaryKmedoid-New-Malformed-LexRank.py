import sys
import re
import fio
import xml.etree.ElementTree as ET
from collections import defaultdict

import random
import NLTKWrapper
import SennaParser
import porter
import phraseClusteringKmedoid

import CourseMirrorSurvey
from CourseMirrorSurvey import maxWeekDict

import postProcess

stopwords = [line.lower().strip() for line in fio.ReadFile("../../ROUGE-1.5.5/data/smart_common_words.txt")]
#print "stopwords:", len(stopwords)

stopwords = stopwords + ['.', '?', '-', ',', '[', ']', '-', ';', '\'', '"', '+', '&', '!', '/', '>', '<', ')', '(', '#', '=']

def getTopRankPhrase(NPs, clusterids, cid, lexdict, sources):
    #get cluster NP, and scores
    dict = {}
    
    s = []
    
    for NP, id, source in zip(NPs, clusterids, sources):
        if int(id) == cid:
            dict[NP] = lexdict[NP.lower()]
            s.append(source)
    
    keys = sorted(dict, key=dict.get, reverse =True)
    
    source = set(s)
    return keys[0], source
                            
def getShallowSummary(excelfile, folder, sennadatadir, clusterdir, K=30, method=None, ratio=None, np=None, lex='lexrank'):
    #K is the number of words per points
    sheets = range(0,maxWeek)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        for type in ['POI', 'MP']:
            print excelfile, sheet, type
            
            student_summaryList = CourseMirrorSurvey.getStudentResponseList(excelfile, course, week, type, withSource=True)
            
            ids = [summary[1] for summary in student_summaryList]
            summaries = [summary[0] for summary in student_summaryList] 
                            
            path = folder + str(week)+ '/'
            fio.NewPath(path)
            filename = path + type + '.summary'
            
            #produce the cluster file on the fly
            sennafile = sennadatadir + "senna." + str(week) + "." + type + '.output'
            output = clusterdir + str(week) +'/' + type + ".cluster.kmedoids." + str(ratio) + "." +method + '.' + np
            weightfile = clusterdir + str(week)+ '/' + type + '.' + np + '.' + method
            if not fio.IsExist(output):
                phraseClusteringKmedoid.getPhraseClusterAll(sennafile, weightfile, output, ratio, MalformedFlilter=True, source=ids, np=np)
            
            NPCandidates, sources = phraseClusteringKmedoid.getNPs(sennafile, MalformedFlilter=True, source=ids, np=np)
            
            #write the sources
            sourcedict = {}
            
            #for np, id in zip(NPCandidates, sources):

            body = fio.ReadMatrix(output, False)
            
            lexfile = clusterdir + str(week)+ '/' + str(type) + "." + np + "."+lex+".dict"
            lexdict = fio.LoadDict(lexfile, 'float')
            
            NPs = [row[0] for row in body]
            clusterids = [row[1] for row in body]
            
            assert(NPCandidates == NPs)
            
            cluster = {}
            for row in body:
                cluster[row[0]] = int(row[1])
            
            Summary = []
            
            #sort the clusters according to the number of phrases
            keys = postProcess.RankCluster(NPs, lexdict, clusterids, sources)
            
                        
            sumarysource = []
            
            total_word = 0
            word_count = 0
            for key in keys:
                #phrase = NPs[key]
                phrase, source = postProcess.getTopRankPhrase(NPs, clusterids, int(key), lexdict, sources)
                if phrase in Summary: continue
                
                word_count = len(phrase.split())
                total_word = total_word + word_count
                #if total_word <= K:
                if len(Summary) + 1 <= K:
                    Summary.append(phrase)
                    sumarysource.append(",".join(source))
            
            fio.SaveList(Summary, filename)
            fio.SaveList(sumarysource, filename + ".source")
            
                        
def ShallowSummary(excelfile, datadir, sennadatadir, clusterdir, K=30, method=None, ratio=None, np=None, lex='lexrank'):
    getShallowSummary(excelfile, datadir, sennadatadir, clusterdir, K, method, ratio, np, lex)

def GetLexRankScore(datadir, np, outputdir):
    sheets = range(0,25)
    
    for type in ['POI', 'MP', 'LP']:
        for sheet in sheets:
            week = sheet + 1
            
            DID = str(week) + '_' + type
            
            phrases = []
            scores = []
    
            #read Docsent
            path = datadir + str(week)+ '/'
            path = path + type + '/'
            path = path + 'docsent/'
            filename = path + DID + '.docsent'
            if not fio.IsExist(filename): continue
            
            tree = ET.parse(filename)
            root = tree.getroot()
            
            for child in root:
                phrases.append(child.text)
            
            #read feature
            path = datadir + str(week)+ '/'
            path = path + type + '/'
            path = path + 'feature/'
            filename = path + type + '.LexRank.sentfeature'
            
            if fio.IsExist(filename):
                tree = ET.parse(filename)
                root = tree.getroot()
                
                for child in root:
                    feature = child[0]
                    #print feature.tag, feature.attrib, feature.attrib['V']
                    #print child.tag, child.attrib
                    scores.append(feature.attrib['V'])
            else:
                for phrase in phrases:
                    scores.append("0")
                
            #write
            assert(len(phrases) == len(scores))
            
            dict = {}
            for phrase, score in zip(phrases, scores):
                dict[phrase.lower()] = score
            
            output = outputdir + str(week)+ '/' + str(type) + "." + np + ".lexrank.dict"
            fio.NewPath(outputdir + str(week)+ '/')
            fio.SaveDict(dict, output, SortbyValueflag=True)
            
            dict = {}
            for phrase, score in zip(phrases, scores):
                if phrase.lower() in dict:
                    dict[phrase.lower()] = max(score, dict[phrase.lower()])
                else:
                    dict[phrase.lower()] = score
            
            output = outputdir + str(week)+ '/' + str(type) + "." + np + ".lexrankmax.dict"
            fio.SaveDict(dict, output, SortbyValueflag=True)
                        
if __name__ == '__main__':
    #Step6: get LSA results
    
    #Step7: Run Clustering
    for c in ["IE256"]:
        course = c
        maxWeek = maxWeekDict[course]
        
        sennadir = "../data/"+course+"/senna/"
        excelfile = "../data/CourseMirror/Reflection.json"
        #phrasedir = "../data/"+course+"/phrases/"
                
        clusterdir = "../data/"+course+"/np/"
        fio.NewPath(clusterdir)
        
        for np in ['syntax']:
            datadir = "../../mead/data/"+course+"_PhraseMead/"
            GetLexRankScore(datadir, np, clusterdir)
            
        for ratio in ["sqrt"]:
            for method in ['optimumComparerLSATasa']:
                for np in ['syntax']:
                    for lex in ['lexrankmax']:
                        datadir = "../../mead/data/"+course+"_ClusterARank/"   
                        fio.DeleteFolder(datadir)
                        ShallowSummary(excelfile, datadir, sennadir, clusterdir, K=4, method=method, ratio=ratio, np=np, lex=lex)
                 
    print "done"
    