import Survey, fio
from OrigReader import prData

import NLTKWrapper

#Write Quality to Weka
def getQuality(excelfile):
    
    Data = []
    
    sheets = range(1,24)
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        MPs = Survey.getMPQualityPoint(orig)
        if len(MPs) == 0:
            print week
        
        Data = Data + MPs
    
    return Data

def getQualityDistribution(excelfile, output):
    MPs = getQuality(excelfile)
    
    dict = {}
    for MP, score in MPs:
        if score not in dict:
            dict[score] = 0
        dict[score] = dict[score] + 1
    
    fio.SaveDict(dict, output, SortbyValueflag = False)

def getQualityText(excelfile, output):
    MPs = getQuality(excelfile)
    
    Text = []
    for MP, _ in MPs:
        MP = ' '.join(NLTKWrapper.wordtokenizer(MP))
        #if len(MP.strip()) == 0: continue
        Text.append(MP)
    
    fio.savelist(Text, output)
    
def PostProcessProb(excelfile, prob, output):
    MPs = getQuality(excelfile)
    
    probs = [line.strip() for line in fio.readfile(prob)]
    
    i = 0
    P = []
    for MP, _ in MPs:
        MP = ' '.join(NLTKWrapper.wordtokenizer(MP))
        if len(MP.strip()) == 0: 
            P.append("0")
            continue
        
        P.append(probs[i])
        i = i + 1
        
    fio.savelist(P, output)
        
def WriteQuality2Weka_WC(excelfile, output):
    MPs = getQuality(excelfile)
    
    head = []
    #head = head + ['Text']
    head = head + ['WC']
    head = head + ['@class@']
    
    types = []
    #types = types + ['String']
    types = types + ['Continuous']
    types = types + ['Category']
    
    data = []
    for MP, score in MPs:
        row = []
        
        MP = ' '.join(NLTKWrapper.wordtokenizer(MP))
        N = len(MP.split())
        
        #row.append(MP)
        row.append(N)
        row.append(score)
        
        data.append(row)
   
    fio.ArffWriter(output, head, types, "Quality", data)

def WriteQuality2Weka_Unigram(excelfile, output):
    MPs = getQuality(excelfile)
    
    head = []
    head = head + ['Text']
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Category']
    
    data = []
    for MP, score in MPs:
        row = []
        
        MP = ' '.join(NLTKWrapper.wordtokenizer(MP))
        N = len(MP.split())
        
        row.append(MP)
        row.append(score)
        
        data.append(row)
   
    fio.ArffWriter(output, head, types, "Quality", data)

def WriteQuality2Weka_SpecitellerProb(excelfile, prob, output):
    probs = [float(line.strip()) for line in fio.readfile(prob)]
    
    MPs = getQuality(excelfile)
    
    head = []
    head = head + ['Prob']
    head = head + ['@class@']
    
    types = []
    types = types + ['Continuous']
    types = types + ['Category']
    
    data = []
    for i, (MP, score) in enumerate(MPs):
        row = []
        
        MP = ' '.join(NLTKWrapper.wordtokenizer(MP))
        N = len(MP.split())
        
        row.append(probs[i])
        row.append(score)
        
        data.append(row)
   
    fio.ArffWriter(output, head, types, "Quality", data)

def WriteQuality2Weka_SpecitellerBinary(excelfile, prob, output):
    probs = [float(line.strip()) for line in fio.readfile(prob)]
    
    MPs = getQuality(excelfile)
    
    head = []
    head = head + ['ProbBinary']
    head = head + ['@class@']
    
    types = []
    types = types + ['Category']
    types = types + ['Category']
    
    data = []
    for i, (MP, score) in enumerate(MPs):
        row = []
        
        MP = ' '.join(NLTKWrapper.wordtokenizer(MP))
        N = len(MP.split())
        
        row.append('1' if probs[i] >= 0.5 else '0')
        row.append(score)
        
        data.append(row)
   
    fio.ArffWriter(output, head, types, "Quality", data)
    
def WriteQuality2Weka_WC_Ngram(excelfile, prob, output):
    probs = [float(line.strip()) for line in fio.readfile(prob)]
    
    MPs = getQuality(excelfile)
    
    head = []
    head = head + ['Text']
    head = head + ['WC']
    #head = head + ['Prob']
    #head = head + ['ProbBinary']
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous']
    #types = types + ['Continuous']
    #types = types + ['Category']
    types = types + ['Category']
    
    data = []
    for i, (MP, score) in enumerate(MPs):
        row = []
        
        MP = ' '.join(NLTKWrapper.wordtokenizer(MP))
        N = len(MP.split())
        
        row.append(MP)
        row.append(N)
        #row.append(probs[i])
        #row.append('1' if probs[i] >= 0.5 else '0')
        row.append(score)
        
        data.append(row)
   
    fio.ArffWriter(output, head, types, "Quality", data)
    
def WriteQuality2Weka_ALL(excelfile, prob, output):
    probs = [float(line.strip()) for line in fio.readfile(prob)]
    
    MPs = getQuality(excelfile)
    
    head = []
    head = head + ['Text']
    head = head + ['WC']
    head = head + ['Prob']
    head = head + ['ProbBinary']
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous']
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    data = []
    for i, (MP, score) in enumerate(MPs):
        row = []
        
        MP = ' '.join(NLTKWrapper.wordtokenizer(MP))
        N = len(MP.split())
        
        row.append(MP)
        row.append(N)
        row.append(probs[i])
        row.append('1' if probs[i] >= 0.5 else '0')
        row.append(score)
        
        data.append(row)
   
    fio.ArffWriter(output, head, types, "Quality", data)
            
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
  
    #dis = "../data/q_dis.txt"
    #getQualityDistribution(excelfile, dis)
    
    text = "../../speciteller/MP.txt"
    prob = "../data/MP.prob"
    #getQualityText(excelfile, text)
    #PostProcessProb(excelfile, "../../speciteller/MP.prob", "../data/MP.prob")
    
#     wekafile = "../data/quality_wc.arff"
#     WriteQuality2Weka_WC(excelfile, wekafile)
#   
#     wekafile = "../data/quality_ngram.arff"
#     WriteQuality2Weka_Unigram(excelfile, wekafile)
#     
#     wekafile = "../data/quality_specitellerProb.arff"
#     WriteQuality2Weka_SpecitellerProb(excelfile, prob, wekafile)
#     
#     wekafile = "../data/quality_specitellerBinary.arff"
#     WriteQuality2Weka_SpecitellerBinary(excelfile, prob, wekafile)
#     
#     wekafile = "../data/quality_all.arff"
#     WriteQuality2Weka_ALL(excelfile, prob, wekafile)

    wekafile = "../data/quality_WC_Ngram.arff"
    #WriteQuality2Weka_WC_Ngram(excelfile, prob, wekafile)

    fio.extractWekaScore("../../QualityPrediction/log.txt", "../data/MP_results.txt")
