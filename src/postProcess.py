from OrigReader import prData
import sys
import re
import fio
import xml.etree.ElementTree as ET
import numpy
from collections import defaultdict
import NLTKWrapper
import phraseClusteringKmedoid
import json
import shallowSummary

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
        print model
        sheets = range(0,12)
        types = ['POI', 'MP', 'LP']
        scores = ['ROUGE-1','ROUGE-2', 'ROUGE-SUX']
        
        #header = ['week', 'R1', 'R2', 'R-SU4', 'R1', 'R2', 'R-SU4', 'R1', 'R2', 'R-SU4']
        header = ['week', 'R1-P', 'R1-R', 'R1-F', 'R2-P', 'R2-R', 'R2-F', 'RSU4-P', 'RSU4-R', 'RSU4-F', 'R1-P', 'R1-R', 'R1-F', 'R2-P', 'R2-R', 'R2-F', 'RSU4-P', 'RSU4-R', 'RSU4-F', 'R1-P', 'R1-R', 'R1-F', 'R2-P', 'R2-R', 'R2-F', 'RSU4-P', 'RSU4-R', 'RSU4-F', ]
        
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
                        score = scorevalues[1].strip()
                        row.append(score)
                        score = scorevalues[2].strip()
                        row.append(score)
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
            row.append(numpy.mean(scores))
        body.append(row)
        
        fio.writeMatrix(outputdir + "rouge." + model + ".txt", body, header)
        
def GetRougeScoreMMR(datadir, models, outputdir): #only keep the average
    for model in models:
        sheets = range(0,12)
        types = ['POI', 'MP', 'LP']
        scores = ['ROUGE-1','ROUGE-2', 'ROUGE-SUX']
        
        header = ['week', 'R1-P', 'R1-R', 'R1-F', 'R2-P', 'R2-R', 'R2-F', 'RSU4-P', 'RSU4-R', 'RSU4-F', 'R1-P', 'R1-R', 'R1-F', 'R2-P', 'R2-R', 'R2-F', 'RSU4-P', 'RSU4-R', 'RSU4-F', 'R1-P', 'R1-R', 'R1-F', 'R2-P', 'R2-R', 'R2-F', 'RSU4-P', 'RSU4-R', 'RSU4-F', ]
        #header = ['lamda', 'R1', 'R2', 'R-SU4', 'R1', 'R2', 'R-SU4', 'R1', 'R2', 'R-SU4']
        averagebody = []
        
        for r in ['0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0']:
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
                            score = scorevalues[1].strip()
                            row.append(score)
                            score = scorevalues[2].strip()
                            row.append(score)
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
                row.append(numpy.mean(ave))
                arow.append(numpy.mean(ave))
            body.append(row)
            averagebody.append(arow)
  
            fio.writeMatrix(outputdir + "rouge." + model + '.' + r + ".txt", body, header)
        
        #get max
        #get the max
        row = []
        row.append("max")
        for i in range(1, len(header)):
            scores = [float(xx[i]) for xx in averagebody]
            row.append(numpy.max(scores))
        averagebody.append(row)
        
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
        print numpy.max(counts[type].values()),'\t',numpy.min(counts[type].values()),'\t',numpy.mean(counts[type].values()),'\t',numpy.median(counts[type].values()),'\t',numpy.std(counts[type].values())
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
        print type,'\t',numpy.max(counts[type].values()),'\t',numpy.min(counts[type].values()),'\t',numpy.mean(counts[type].values()),'\t',numpy.median(counts[type].values()),'\t',numpy.std(counts[type].values())

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
        
            row.append(numpy.mean(counts[type].values()))
            row.append(numpy.std(counts[type].values()))
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
        print numpy.max(counts[type].values()),'\t',numpy.min(counts[type].values()),'\t',numpy.mean(counts[type].values()),'\t',numpy.median(counts[type].values()),'\t',numpy.std(counts[type].values())
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

def ExtractNP(datadir, outdir, method="syntax"):
    sheets = range(0,12)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        for type in ['POI', 'MP', 'LP']:
            
            file = datadir + str(week)+ '/' + type + '.summary.keys'
            
            dict = fio.LoadDict(file, 'float')
            keys = sorted(dict, key=dict.get, reverse = True)
            
            fio.newPath(outdir + str(week)+ '/')
            output = outdir + str(week)+ '/' + type + '.'+method+'.key'
            fio.savelist(keys, output)

def ExtractNPSource(excelfile, sennadatadir, outdir, method="syntax"):
    sheets = range(0,12)
    
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            
            sennafile = sennadatadir + "senna." + str(week) + "." + type + '.output'
            
            student_summaryList = getStudentResponseList(orig, header, summarykey, type, withSource=True)
            ids = [summary[1] for summary in student_summaryList]
            NPs, sources = phraseClusteringKmedoid.getNPs(sennafile, MalformedFlilter=False, source=ids, np=method)
            
            dict = {}
            for np, id in zip(NPs, sources):
                if np not in dict:
                    dict[np] = []
                dict[np].append(id)
            
            fileout = outdir + str(week)+ '/' + type + '.'+method+'.keys.source'
            
            with open(fileout, 'w') as outfile:
                json.dump(dict, outfile)

def ExtractUnigramSource(excelfile, outdir, method="unigram"):
    sheets = range(0,12)
    
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            
            sennafile = sennadatadir + "senna." + str(week) + "." + type + '.output'
            
            student_summaryList = getStudentResponseList(orig, header, summarykey, type, withSource=True)
            
            dict = {}
            for summary, id in student_summaryList:
                ngrams = NLTKWrapper.getNgram(summary, 1)
                for ngram in ngrams:
                    ngram = ngram.lower()
                    if ngram not in dict:
                        dict[ngram] = []
                    dict[ngram].append(id)
            
            fileout = outdir + str(week)+ '/' + type + '.'+method+'.keys.source'
            
            with open(fileout, 'w') as outfile:
                json.dump(dict, outfile)
               
def CombineKMethod(datadir, output, methods, ratios, nps, model_prefix):
    Header = ['np', 'method', 'lambda', 'R1', 'R2', 'R-SU4', 'R1', 'R2', 'R-SU4', 'R1', 'R2', 'R-SU4']
    newbody = []
    
    for np in nps:
        for method in methods: 
            for ratio in ratios:
                filename = datadir + "rouge." + model_prefix + "_" + str(ratio) + "_"+ method + '_' + np + ".txt"
                head, body = fio.readMatrix(filename, hasHead=True)
                
                row = []
                row.append(np)
                row.append(method)
                row.append(ratio)
                row = row + body[-1][1:]
                
                newbody.append(row)
            
    #get the max
    row = []
    row.append("max")
    row.append("")
    row.append("")
    for i in range(3, len(Header)):
        scores = [float(xx[i]) for xx in newbody]
        row.append(numpy.max(scores))
    newbody.append(row)
    
    fio.writeMatrix(output, newbody, Header)
    
def CombineRouges(models, outputdir):
    Header = ['method', 'R1-P', 'R1-R', 'R1-F', 'R2-P', 'R2-R', 'R2-F', 'RSU4-P', 'RSU4-R', 'RSU4-F', 'R1-P', 'R1-R', 'R1-F', 'R2-P', 'R2-R', 'R2-F', 'RSU4-P', 'RSU4-R', 'RSU4-F', 'R1-P', 'R1-R', 'R1-F', 'R2-P', 'R2-R', 'R2-F', 'RSU4-P', 'RSU4-R', 'RSU4-F', ]
    newbody = []
    
    for model in models: 
        filename = outputdir + "rouge." + model + ".txt"
        head, body = fio.readMatrix(filename, hasHead=True)
        
        row = []
        row.append(model)
        row = row + body[-1][1:]
        
        newbody.append(row)
            
    #get the max
    row = []
    row.append("max")
    for i in range(1, len(Header)):
        scores = [float(xx[i]) for xx in newbody]
        row.append(numpy.max(scores))
    newbody.append(row)
    
    newname = outputdir + "_".join(models) + ".txt"
    if len(newname) > 50:
        newname = newname[:50] + "_50.txt"
    fio.writeMatrix(newname, newbody, Header)    

def getSingleCoverage(entries, sources, N):
    covered = []
    
    for entry in entries:
        if entry not in sources:
            print entry
            continue
        covered = covered + sources[entry]

    return len(set(covered))*1.0/N

def getSingleQuality(entries, sources, qualitydict, N):
    scores = []
    for entry in entries:
        if entry not in sources:
            print entry
            continue
        
        score = 0.0
        for id in sources[entry]:
            if id not in qualitydict: continue
            if qualitydict[id] == 'a': continue
            
            score = score + float(qualitydict[id])
        score = score / len(sources[entry])
        
        scores.append(score)

    return numpy.mean(scores)

def getSingleDiversity(entries, sources):
    covered = []
    
    for entry in entries:
        if entry not in sources:
            print entry
            continue
        covered = covered + sources[entry]
        
    covered = set(covered) #get all covered students
    
    #for each of the student, get the probability
    dict = defaultdict(float)
    for entry in entries:
        if entry not in sources:continue
        ids = sources[entry]
        
        for id in ids:
            dict[id] = dict[id] + 1.0
    
    N = len(covered)
    
    for k, v in dict.items():#normailize to probablity
        dict[k] = v/N
        assert(dict[k] <= 1.0)
    
    #get the entropy
    entropy = 0
    for k, v in dict.items(): #normailize to probablity
        entropy = entropy - v * numpy.log(v)
        
    return entropy

def getCoverage(modelname, excelfile, npdir, method="unigram"):
    sheets = range(0,12)
    
    newhead = ['week', 'POI', 'MP', 'LP']
    newbody = []
    
    datadir = "../../mead/data/" + modelname + '/'
    
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        orig = prData(excelfile, sheet)
        
        row = []
        row.append(week)
        
        for type in ['POI', 'MP', 'LP']:
            path = datadir + str(week)+ '/'
            summaryfile = path + type + '.summary'
            summaries = [line.strip() for line in fio.readfile(summaryfile)]
            
            sourcefile = npdir + str(week)+ '/' + type + '.'+method+'.keys.source'
            student_summaryList = getStudentResponseList(orig, header, summarykey, type, withSource=True)
            N = getValidStudentNum(student_summaryList)
            
            print sourcefile, summaryfile
            
            with open(sourcefile, 'r') as infile:
                dict = json.load(infile)
            
            coverage = getSingleCoverage(summaries, dict, N)
            assert(coverage <= 1.0)
            row.append(coverage)
        
        newbody.append(row)
    
    row = []
    row.append("average")
    for i in range(1, len(newhead)):
        scores = [float(xx[i]) for xx in newbody]
        row.append(numpy.mean(scores))
    newbody.append(row)
        
    file = "../data/coverage." + modelname + '.txt'
    fio.writeMatrix(file, newbody, newhead)

def getDiversity(modelname, excelfile, npdir, method="unigram"):
    sheets = range(0,12)
    
    newhead = ['week', 'POI', 'MP', 'LP']
    newbody = []
    
    datadir = "../../mead/data/" + modelname + '/'
    
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        orig = prData(excelfile, sheet)
        
        row = []
        row.append(week)
        
        for type in ['POI', 'MP', 'LP']:
            path = datadir + str(week)+ '/'
            summaryfile = path + type + '.summary'
            summaries = [line.strip() for line in fio.readfile(summaryfile)]
            
            sourcefile = npdir + str(week)+ '/' + type + '.'+method+'.keys.source'
            student_summaryList = getStudentResponseList(orig, header, summarykey, type, withSource=True)
            N = getValidStudentNum(student_summaryList)
            
            print sourcefile, summaryfile
            
            with open(sourcefile, 'r') as infile:
                dict = json.load(infile)
            
            diversity = getSingleDiversity(summaries, dict)
            row.append(diversity)
        
        newbody.append(row)
    
    row = []
    row.append("average")
    for i in range(1, len(newhead)):
        scores = [float(xx[i]) for xx in newbody]
        row.append(numpy.mean(scores))
    newbody.append(row)
        
    file = "../data/diversity." + modelname + '.txt'
    fio.writeMatrix(file, newbody, newhead)

def getHighQualityRatio(modelname, excelfile, npdir, method="unigram"):
    sheets = range(0,12)
    
    newhead = ['week', 'MP']
    newbody = []
    
    datadir = "../../mead/data/" + modelname + '/'
    
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        orig = prData(excelfile, sheet)
        
        row = []
        row.append(week)
        
        for type in ['MP']:
            path = datadir + str(week)+ '/'
            summaryfile = path + type + '.summary'
            summaries = [line.strip() for line in fio.readfile(summaryfile)]
            
            qualitydict = getStudentQuality(orig, header)
            
            sourcefile = npdir + str(week)+ '/' + type + '.'+method+'.keys.source'
            student_summaryList = getStudentResponseList(orig, header, summarykey, type, withSource=True)
            N = getValidStudentNum(student_summaryList)
            
            print sourcefile, summaryfile
            
            with open(sourcefile, 'r') as infile:
                dict = json.load(infile)
            
            coverage = getSingleQuality(summaries, dict, qualitydict, N)
            row.append(coverage)
        
        newbody.append(row)
    
    row = []
    row.append("average")
    for i in range(1, len(newhead)):
        scores = [float(xx[i]) for xx in newbody]
        row.append(numpy.mean(scores))
    newbody.append(row)
        
    file = "../data/quality." + modelname + '.txt'
    fio.writeMatrix(file, newbody, newhead)
            
def getCoverageDiversity(modelname, excelfile, npdir, method="unigram"):
    getCoverage(modelname, excelfile, npdir, method)
    getDiversity(modelname, excelfile, npdir, method)
    getHighQualityRatio(modelname, excelfile, npdir, method)

def PrintCluster(output):
    body = fio.readMatrix(output, False)
            
    NPs = [row[0] for row in body]
    clusterids = [row[1] for row in body]
    
    cluster = {}
    for row in body:
        cluster[row[0]] = int(row[1])
    
    Summary = []
    
    #sort the clusters according to the number of phrases
    dict = defaultdict(float)
    for row in body: 
        dict[int(row[1])] = dict[int(row[1])] + 1
    
    keys = sorted(dict, key=dict.get, reverse =True)
    
    clusters = []
    dict = {}
    for key in keys:
        
        #get the phrases
        P = []
        P.append(NPs[key])
        
        for i, (NP, id) in enumerate(zip(NPs, clusterids)):
            if i == key: continue
            if int(id) == key:
                P.append(NP)
        clusters.append(P)
    
    for i, cluster in enumerate(clusters):
        print i+1, '\t', len(cluster), '\t', ', '.join(cluster)
                                      
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
    
    sennadatadir = "../data/senna/"
    
    npdir = "../data/np/"
    #ExtractUnigramQuality(excelfile, sennadatadir, npdir, 'syntax')
    
#     modelname = 'ShallowSummary_unigram_remove_stop'
#     #getCoverageDiversity(modelname, excelfile, npdir, method = 'unigram')
#     getHighQualityRatio(modelname, excelfile, npdir, method = 'unigram')
#      
#     modelname = 'ShallowSummary_ClusteringNP_KMedoidMalformedKeyphrase_0.6_npsoft_chunk'
#     #getCoverageDiversity(modelname, excelfile, npdir, method = 'chunk')
#     getHighQualityRatio(modelname, excelfile, npdir, method = 'chunk')
#       
#     modelname = 'ShallowSummary_ClusteringNP_KMedoidMalformedKeyphrase_0.2_optimumComparerLSATasa_chunk'
#     #getCoverageDiversity(modelname, excelfile, npdir, method = 'chunk')
#     getHighQualityRatio(modelname, excelfile, npdir, method = 'chunk')
    
    #datadir = '../data/ShallowSummary_unigram_remove_stop.txt'
    #getCoverage(excelfile, npdir, output, method = 'unigram')
    
    
    #ExtractNPSource(excelfile, sennadatadir, outdir, 'syntax')
    #ExtractNPSource(excelfile, sennadatadir, outdir, 'chunk')
    #ExtractUnigramSource(excelfile, outdir)
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
    #ShallowSummary_ClusteringNP_KMedoid_sqrt_lexicalOverlapComparer
    #ShallowSummary_ClusteringNP_KMedoid_sqrt_npsoft
    #'PhraseMead_chunk', 'PhraseMead_syntax', 'PhraseMead_candidate', 'PhraseMead_candidatestemming'
    
    #PrintCluster("../data/np/3/MP.cluster.kmedoids.sqrt.optimumComparerLSATasa.syntax")
    
    models = ['ShallowSummary_unigram', #'ShallowSummary_unigram_remove_stop', 'ShallowSummary_unigram_tfidf',
              #'ShallowSummary_bigram',
              #'keyphraseExtractionbasedShallowSummary',
              #'ShallowSummary_NPhrase_chunk_TFIDF', 'ShallowSummary_NPhrase_syntax_TFIDF',
              #'PhraseMead_chunk', 'PhraseMead_syntax', 
              #'PhraseMeadLexRank_chunk', 'PhraseMeadLexRank_syntax', 
              #'Clustering_lexrank_sqrt_npsoft_chunk', 'Clustering_lexrank_sqrt_npsoft_syntax', 'Clustering_lexrank_sqrt_optimumComparerLSATasa_chunk', 'Clustering_lexrank_sqrt_optimumComparerLSATasa_syntax',
              #'Clustering_lexrankmax_sqrt_npsoft_chunk', 'Clustering_lexrankmax_sqrt_npsoft_syntax', 'Clustering_lexrankmax_sqrt_optimumComparerLSATasa_chunk', 'Clustering_lexrankmax_sqrt_optimumComparerLSATasa_syntax',
              #'ShallowSummary_ClusteringNP_KMedoid_sqrt_lexicalOverlapComparer'
              #'ShallowSummary_ClusteringNP_KMedoidMalformedKeyphrase_LexRank_sqrt_optimumComparerLSATasa_syntax', 'ShallowSummary_ClusteringNP_KMedoidMalformedKeyphrase_LexRank_sqrt_optimumComparerLSATasa_chunk', 'ShallowSummary_ClusteringNP_KMedoidMalformedKeyphrase_LexRank_sqrt_npsoft_syntax', 'ShallowSummary_ClusteringNP_KMedoidMalformedKeyphrase_LexRank_sqrt_npsoft_chunk',
              #'Phrase_syntax_lexrank', 'Phrase_chunk_lexrank',
              #'PhraseLexRankMMR_chunk', 'PhraseLexRankMMR_syntax',
              #'PhraseMead_syntax', 'PhraseMead_chunk', 'PhraseMeadLexRank_syntax', 'PhraseMeadLexRank_chunk',
              
              #'C4_ShallowSummary_unigram',
              #'C4_ShallowSummary_bigram',
              #'C4_Phrase_syntax_lexrank', 'C4_Phrase_chunk_lexrank',
              #'C4_Clustering_lexrankmax_sqrt_npsoft_chunk', 'C4_Clustering_lexrankmax_sqrt_npsoft_syntax', 'C4_Clustering_lexrankmax_sqrt_optimumComparerLSATasa_chunk', 'C4_Clustering_lexrankmax_sqrt_optimumComparerLSATasa_syntax',
              #'C4_Clustering_lexrankmax_sqrt_optimumComparerLSATasa_syntax',
              ]
    GetRougeScore(datadir = "../../mead/data/", models = models, outputdir = "../data/" )
    CombineRouges(models = models, outputdir = "../data/")
    
    #GetRougeScoreMMR(datadir = "../../mead/data/", models = ['PhraseMeadLexRankMMR_syntax', 'PhraseMeadLexRankMMR_chunk', 'PhraseMeadMMR_syntax', 'PhraseMeadMMR_chunk'], outputdir = "../data/")
       
    #GetRougeScore(datadir = "../../mead/data/", model = "2011Spring", outputdir = "../data/" )
    #GetRougeScore(datadir, rougescore)
    #TASummaryCoverage(excelfile, datadir, output="../data/coverage.txt")
    #print getNgram("1 2 3 4 5 6", 6)

    
#     datadir = "../../mead/data/ShallowSummary_PhraseCandidateSoft_default/"
#     outdir = "../data/np/"
#     ExtractNP(datadir, outdir, 'candidate')
#    
    
    #methods = ['npsoft', 'greedyComparerWNLin', 'optimumComparerLSATasa','optimumComparerWNLin',  'dependencyComparerWnLeskTanim', 'lexicalOverlapComparer']
#     methods = ['npsoft', 'optimumComparerLSATasa']
#     ratios = ["sqrt", 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
#     nps = ['chunk', 'syntax','candidate', 'candidatestemming', 'candidatengram', 'candidatengramstemming']
#     #ShallowSummary_ClusteringNP_KMedoid, ShallowSummary_ClusteringNP_KMedoidMalformedKeyphrase
#     for ratio in ratios:
#         for method in methods: #'bleuComparer', 'cmComparer', 'lsaComparer',
#             for np in nps:
#                 GetRougeScore(datadir = "../../mead/data/", models = ['ShallowSummary_ClusteringNP_KMedoidMalformedKeyphrase' + "_"+ str(ratio)+"_"+method+"_"+np], outputdir = "../data/" )
#        
#     CombineKMethod("../data/", "../data/Kmetroid-K-Method-NP-KMedoidMalformedKeyphrase.txt", methods, ratios, nps, 'ShallowSummary_ClusteringNP_KMedoidMalformedKeyphrase')
#   
 
    print "done"