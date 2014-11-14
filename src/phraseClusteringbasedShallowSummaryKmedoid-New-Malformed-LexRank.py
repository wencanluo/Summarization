import sys
import re
import fio
import xml.etree.ElementTree as ET
from collections import defaultdict
from Survey import *
import random
import NLTKWrapper
import SennaParser
import porter
import phraseClusteringKmedoid

stopwords = [line.lower().strip() for line in fio.readfile("../../ROUGE-1.5.5/data/smart_common_words.txt")]
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
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    #sheets = range(0,12)
    sheets = range(0,12)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            print excelfile, sheet, type
            
            if week == 3 and type == 'MP' and np == 'syntax' and method == 'optimumComparerLSATasa':
                debug = 0
                
            student_summaryList = getStudentResponseList(orig, header, summarykey, type, withSource=True)
            
            ids = [summary[1] for summary in student_summaryList]
            summaries = [summary[0] for summary in student_summaryList] 
                            
            path = folder + str(week)+ '/'
            fio.newPath(path)
            filename = path + type + '.summary'
            
            #produce the cluster file on the fly
            sennafile = sennadatadir + "senna." + str(week) + "." + type + '.output'
            output = clusterdir + str(week) +'/' + type + ".cluster.kmedoids." + str(ratio) + "." +method + '.' + np
            weightfile = clusterdir + str(week)+ '/' + type + '.' + np + '.' + method
            if not fio.isExist(output):
                phraseClusteringKmedoid.getPhraseClusterAll(sennafile, weightfile, output, ratio, MalformedFlilter=True, source=ids, np=np)
            
            NPCandidates, sources = phraseClusteringKmedoid.getNPs(sennafile, MalformedFlilter=True, source=ids, np=np)
            
            #write the sources
            sourcedict = {}
            
            #for np, id in zip(NPCandidates, sources):

            body = fio.readMatrix(output, False)
            
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
            dict = defaultdict(float)
            for row in body: 
                dict[int(row[1])] = dict[int(row[1])] + 1
            
            keys = sorted(dict, key=dict.get, reverse =True)
            
            sumarysource = []
            
            total_word = 0
            word_count = 0
            for key in keys:
                #phrase = NPs[key]
                phrase, source = getTopRankPhrase(NPs, clusterids, key, lexdict, sources)
                if phrase in Summary: continue
                
                word_count = len(phrase.split())
                total_word = total_word + word_count
                #if total_word <= K:
                if len(Summary) + 1 <= K:
                    Summary.append(phrase)
                    sumarysource.append(",".join(source))
            
            fio.savelist(Summary, filename)
            fio.savelist(sumarysource, filename + ".source")
            
                        
def ShallowSummary(excelfile, datadir, sennadatadir, clusterdir, K=30, method=None, ratio=None, np=None, lex='lexrank'):
    getShallowSummary(excelfile, datadir, sennadatadir, clusterdir, K, method, ratio, np, lex)
    WriteTASummary(excelfile, datadir)

def GetLexRankScore(datadir, np, outputdir):
    sheets = range(0,12)
    
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
            
            tree = ET.parse(filename)
            root = tree.getroot()
            
            for child in root:
                phrases.append(child.text)
            
            #read feature
            path = datadir + str(week)+ '/'
            path = path + type + '/'
            path = path + 'feature/'
            filename = path + type + '.LexRank.sentfeature'
            
            tree = ET.parse(filename)
            root = tree.getroot()
            
            for child in root:
                feature = child[0]
                #print feature.tag, feature.attrib, feature.attrib['V']
                #print child.tag, child.attrib
                scores.append(feature.attrib['V'])
                
            #write
            assert(len(phrases) == len(scores))
            
            dict = {}
            for phrase, score in zip(phrases, scores):
                dict[phrase.lower()] = score
            
            output = outputdir + str(week)+ '/' + str(type) + "." + np + ".lexrank.dict"
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
    excelfile = "../data/2011Spring.xls"
    
    sennadatadir = "../data/senna/"
    clusterdir = "../data/np/"
    
    for np in ['chunk', 'syntax']:
        datadir = "../../mead/data/PhraseMeadLexRank_"+np+"/"
        GetLexRankScore(datadir, np, clusterdir)
        
    for ratio in ["sqrt"]:
    #for ratio in ["sqrt", 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        #for method in ['optimumComparerLSATasa']: #'bleuComparer', 'cmComparer', 'lsaComparer',
        #for method in ['dependencyComparerWnLeskTanim']:
        for method in ['npsoft', 'optimumComparerLSATasa']:
        #for method in ['optimumComparerLSATasa']:
            for np in ['chunk', 'syntax']:
            #for np in ['syntax']:
                #for lex in ['lexrank', 'lexrankmax']:
                for lex in ['lexrankmax']:
                    datadir = "../../mead/data/C4_Clustering_"+lex+"_"+str(ratio)+"_"+method+"_"+np+"/"   
                    fio.deleteFolder(datadir)
                    ShallowSummary(excelfile, datadir, sennadatadir, clusterdir, K=4, method=method, ratio=ratio, np=np, lex=lex)
            
    print "done"
    