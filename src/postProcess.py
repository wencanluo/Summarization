from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET
import numpy as np
from collections import defaultdict
import NLTKWrapper

from Survey import *
                    
def formatSummaryOutput(excelfile, datadir, output):
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    sheets = range(0,12)
    
    datahead = ['Week', '# of sentence POI', '# of sentence POI', '# of sentence POI']
    
    head = ['Week', 'TA:POI', 'S:POI','TA:MP','S:MP','TA:LP', 'S:LP',]
    body = []
    
    for sheet in sheets:
        row = []
        week = sheet + 1
        row.append(week)
            
        for type in ['POI', 'MP', 'LP']:
            summaries = getMeadSummary(datadir, type)
            
            orig = prData(excelfile, sheet)
        
            summary = getTASummary(orig, header, summarykey, type)
            if summary == []:
                row.append("")
            else:
                row.append(";".join(summary))
                
            summary = ";".join(summaries[sheet])
            row.append(summary)
        
        body.append(row)
            
    fio.writeMatrix(output, body, head)

def GetRougeScore(datadir, models, outputdir):
    for model in models:
        sheets = range(0,12)
        types = ['POI', 'MP', 'LP']
        scores = ['ROUGE-1','ROUGE-2', 'ROUGE-SUX']
        
        header = ['week', 'R1', 'R2', 'R-SU4', 'R1', 'R2', 'R-SU4', 'R1', 'R2', 'R-SU4']
        
        body = []
        for sheet in sheets:
            week = sheet + 1
            path = datadir + model + '/' + str(week)+ '/'
            fio.newPath(path)
            
            row = []
            row.append(week)
            for type in types:
                for scorename in scores:
                    filename = path + type + "_OUT_"+scorename+".csv"
                    lines = fio.readfile(filename)
                    try:
                        scorevalues = lines[1].split(',')
                        score = scorevalues[3].strip()
                        row.append(score)
                    except Exception:
                        print filename, scorename, lines
            body.append(row)
        
        #get average
        
        row = []
        row.append("average")
        for i in range(1, len(header)):
            scores = [float(xx[i]) for xx in body]
            row.append(np.mean(scores))
        body.append(row)
        
        fio.writeMatrix(outputdir + "rouge." + model + ".txt", body, header)
        
def GetRougeScoreMMR(datadir, models, outputdir): #only keep the average
    for model in models:
        sheets = range(0,12)
        types = ['POI', 'MP', 'LP']
        scores = ['ROUGE-1','ROUGE-2', 'ROUGE-SUX']
        
        header = ['lamda', 'R1', 'R2', 'R-SU4', 'R1', 'R2', 'R-SU4', 'R1', 'R2', 'R-SU4']
        averagebody = []
        
        for r in ['0', '0.2', '0.4', '0.6', '0.8', '1.0']:
            body = []
            for sheet in sheets:
                week = sheet + 1
                path = datadir + model + '/' + str(week)+ '/'
                fio.newPath(path)
                
                row = []
                row.append(week)
                for type in types:
                    for scorename in scores:
                        filename = path + type + "." + str(r) + "_OUT_"+scorename+".csv"
                        lines = fio.readfile(filename)
                        try:
                            scorevalues = lines[1].split(',')
                            score = scorevalues[3].strip()
                            row.append(score)
                        except Exception:
                            print filename, scorename, lines
                body.append(row)
            
            #get average
            
            row = []
            row.append("average")
            arow = []
            arow.append('mmr_lambda_'+r)
            for i in range(1, len(header)):
                ave = [float(xx[i]) for xx in body]
                row.append(np.mean(ave))
                arow.append(np.mean(ave))
            body.append(row)
            averagebody.append(arow)
  
            fio.writeMatrix(outputdir + "rouge." + model + '.' + r + ".txt", body, header)
        fio.writeMatrix(outputdir + "rouge." + model + ".txt", averagebody, header)
           
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
    
def getTAWordCountDistribution(excelfile, output):
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    sheets = range(0,12)
    
    datahead = ['Week', '# of sentence POI', '# of sentence POI', '# of sentence POI']
    
    counts = {'POI':{}, 'MP':{}, 'LP':{}}
    for sheet in sheets:
        row = []
        week = sheet + 1
        
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            summaryList = getTASummary(orig, header, summarykey, type)
            for summary in summaryList:
                counts[type][summary]  = len(summary.split())
    
    for type in ['POI', 'MP', 'LP']:
        print np.max(counts[type].values()),'\t',np.min(counts[type].values()),'\t',np.mean(counts[type].values()),'\t',np.median(counts[type].values()),'\t',np.std(counts[type].values())
        #fio.PrintList(counts[type].values(), sep='\t')
        #fio.PrintDict(counts[type], True)
        #print

def getMeadAverageWordCount(summary, output):
    counts = {'POI':{}, 'MP':{}, 'LP':{}}
    
    for type in ['POI', 'MP', 'LP']:
        summaries = getMeadSummary(datadir, type)
        for weeksummary in summaries:
            for summary in weeksummary:
                counts[type][summary]=len(summary.split())
    
    fio.PrintList(["Type", "Max", "Min", "Mean", "Median", "Std"], "\t")
    for type in ['POI', 'MP', 'LP']:
        #fio.PrintList(counts[type].values(), sep=',')
        print type,'\t',np.max(counts[type].values()),'\t',np.min(counts[type].values()),'\t',np.mean(counts[type].values()),'\t',np.median(counts[type].values()),'\t',np.std(counts[type].values())

def getStudentResponseAverageWords(excelfile, output):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    sheets = range(0,12)
    
    body = []
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        counts = {'POI':{}, 'MP':{}, 'LP':{}}
        
        row = []
        row.append(week)
        
        for type in ['POI', 'MP', 'LP']:
            summaries = getStudentResponse(orig, header, summarykey, type=type)
            for summaryList in summaries.values():
                for s in summaryList:
                    counts[type][s] = len(s.split())
        
            row.append(np.mean(counts[type].values()))
            row.append(np.std(counts[type].values()))
        body.append(row)
            
    fio.writeMatrix(output, body, ['Week', 'POI', '', 'MP', '', 'LP', '']) 

def getStudentResponseWordCountDistribution(excelfile, output):
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    #sheets = range(0,25)
    sheets = range(0,25)
    
    counts = {'POI':{}, 'MP':{}, 'LP':{}}
    
    body = []
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        row = []
        for type in ['POI', 'MP', 'LP']:
            summaries = getStudentResponse(orig, header, summarykey, type=type)
            for summaryList in summaries.values():
                for s in summaryList:
                    counts[type][s] = len(s.split())
            
    for type in ['POI', 'MP', 'LP']:
    #for type in ['LP']:
        print np.max(counts[type].values()),'\t',np.min(counts[type].values()),'\t',np.mean(counts[type].values()),'\t',np.median(counts[type].values()),'\t',np.std(counts[type].values())
        #fio.PrintList(counts[type].values(), sep=',')
        #fio.PrintDict(counts[type], True)
        #print

def CheckKeyword(keyword, sentences):
    for s in sentences:
        if s.lower().find(keyword.lower()) != -1:
            return True
    return False
    
def TASummaryCoverage(excelfile, datadir, output):
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    sheets = range(0,12)
    
    datahead = ['Week', '# of sentence POI', '# of sentence POI', '# of sentence POI']
    
    head = ['Week', 'TA:POI', 'S:POI','TA:MP','S:MP','TA:LP', 'S:LP',]
    body = []
    
    MaxNgram = 5
    dict = {'POI':{}, 'MP':{}, 'LP':{}}
    
    uncoveried = defaultdict(float)
    
    for type in ['POI', 'MP', 'LP']:
        for n in range(MaxNgram):
            dict[type][n+1] = [0,0]
    
    for sheet in sheets:
        row = []
        week = sheet + 1
        row.append(week)
        
        for type in ['POI', 'MP', 'LP']:
            orig = prData(excelfile, sheet)
        
            student_summaries = getStudentResponse(orig, header, summarykey, type)
            student_summaryList = []
            
            for summaryList in student_summaries.values():
                for s in summaryList:
                    student_summaryList.append(s)
            
            ta_summaries = getTASummary(orig, header, summarykey, type)
            
            for summary in ta_summaries:
                for n in range(MaxNgram):
                    ngrams = NLTKWrapper.getNgram(summary, n+1)
                    dict[type][n+1][0] = dict[type][n+1][0] + len(ngrams)
                    
                    for token in ngrams:
                        if CheckKeyword(token, student_summaryList):
                            dict[type][n+1][1] = dict[type][n+1][1] + 1
                        else:
                            uncoveried[token.lower()] = uncoveried[token.lower()] + 1
        
    fio.PrintList(["Type", "N", "# of points", "# of response points", "coverage ratio"])
    for type in ['POI', 'MP', 'LP']:
        for n in range(MaxNgram):
            print type, "\t", n+1, "\t", dict[type][n+1][0], "\t", dict[type][n+1][1], "\t", float(dict[type][n+1][1])/dict[type][n+1][0]
    
    fio.PrintDict(uncoveried, True)

def ExtractedSyntaxNP(datadir, outdir):
    sheets = range(0,12)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        for type in ['POI', 'MP', 'LP']:
            file = datadir + str(week)+ '/' + type + '.summary.keys'
            
            dict = fio.LoadDict(file, 'float')
            keys = sorted(dict, key=dict.get, reverse = True)
            
            output = outdir + str(week)+ '/' + type + '.key'
            fio.savelist(keys, output)
                
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    output = "../data/2011Spring_overivew.txt"
    summaryoutput = "../data/2011Spring_summary.txt"
    
    
    #datadir_multiple = "../../mead/data/2011SpringMutiple/"
    
    #formatedsummary = '../data/2011Spring_Mead_multiplesummary.txt'
    formatedsummary = '../data/2011Spring_Mead_summary.txt'
    TAwordcount = '../data/2011Spring_ta_wordcount.txt'
    
    rougescore = "../data/2011Spring_rouge_single.txt"
    rougescore_multiple = "../data/2011Spring_rouge_multiple.txt"
    
    #load(excelfile, output)
    #getSummaryOverview(excelfile, summaryoutput)
    
    #Write2Mead(excelfile, datadir)
    #formatSummaryOutput(excelfile, datadir_multiple, output=formatedsummary)
    #formatSummaryOutput(excelfile, datadir, output=formatedsummary)
    #getTAWordCountDistribution(excelfile, TAwordcount)
    #getWordCount(formatedsummary, TAwordcount)
    #getMeadAverageWordCount(formatedsummary, '../data/2011Spring_mead_avaregewordcount.txt')
    #getStudentResponseAverageWords(excelfile, '../data/averageword.txt')
    #getStudentResponseWordCountDistribution(excelfile, '../data/studentword_distribution.txt')
    #GetRougeScore(datadir_multiple, rougescore_multiple)
    #GetRougeScore(datadir = "../../mead/data/", models = ['2011Spring', 'RandombaselineK3', 'RandombaselineK2', 'RandombaselineK1', 'LongestbaselineK3', 'LongestbaselineK2', 'LongestbaselineK1', 'ShortestbaselineK3', 'ShortestbaselineK2', 'ShortestbaselineK1'], outputdir = "../data/" )
    #GetRougeScore(datadir = "../../mead/data/", models = ['TopicWordStem', 'ShallowSummary_bigram_remove_stop','ShallowSummary_weightedngram_remove_stop','ShallowSummary_unigram_remove_stop', 'ShallowSummary_ngram_remove_stop'], outputdir = "../data/" )
    #'ShallowbasedExtrativeSummary_topicS', 'ShallowbasedExtrativeSummary_unigram'
    #ShallowSummary_NPhraseHard ShallowSummary_NPhraseSoft
    #'ShallowSummary_unigram_tfidf'
    #'ShallowSummary_nphard', 'ShallowSummary_npsoft', 'ShallowSummary_greedyComparerWNLin'
    #'ShallowSummary_WeightedgreedyComparerWNLin', 'ShallowSummary_WeightedoptimumComparerWNLin', 'ShallowSummary_WeightedoptimumComparerLSATasa', 'ShallowSummary_WeighteddependencyComparerWnLeskTanim', 'ShallowSummary_WeightedlsaComparer', 'ShallowSummary_WeightedbleuComparer', 'ShallowSummary_WeightedcmComparer', 'ShallowSummary_WeightedlexicalOverlapComparer'
    #'ShallowSummary_AdjNounPhrase_Hard_NoSingleNoun', 'ShallowSummary_AdjNounPhrase_Hard_WithSingleNoun', 'ShallowSummary_AdjNounPhrase_Soft_NoSingleNoun', 'ShallowSummary_AdjNounPhrase_Soft_WithSingleNoun'
    #'ShallowSummary_SyntaxNPhraseHard', 'ShallowSummary_SyntaxNPhraseSoft'
    #'ShallowSummary_ClusteringNPhraseSoft', ShallowSummary_ClusteringSyntaxNPhraseSoft
    GetRougeScore(datadir = "../../mead/data/", models = ['ShallowSummary_ClusteringNPhraseSoftKMedoid'], outputdir = "../data/" )
    #GetRougeScoreMMR(datadir = "../../mead/data/", models = ['2011SpringReranker'], outputdir = "../data/")
    #GetRougeScore(datadir = "../../mead/data/", model = "2011Spring", outputdir = "../data/" )
    #GetRougeScore(datadir, rougescore)
    #TASummaryCoverage(excelfile, datadir, output="../data/coverage.txt")
    #print getNgram("1 2 3 4 5 6", 6)
    
    datadir = "../../mead/data/ShallowSummary_NPhraseSoft/"
    outdir = "../data/np/"
    #ExtractedSyntaxNP(datadir, outdir)
    
    print "done"