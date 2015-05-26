import sys, fio
import QualityPrediction
import Survey
import NLTKWrapper
from collections import defaultdict

class_label = '@class@'

def getBinaryFeatures(excelfile, prob, titledir, output):
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = QualityPrediction.getQualitywithLecture(excelfile)
    
    head = []
    #head = head + ['Text'] #ngram
    #head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    head = head + ['OrgAssign']
    head = head + ['Title']
    #head = head + ['WCTitle']
    #head = head + ['RatioTitle']

    #head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    #types = types + ['String']
    #types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    types = types + ['Category']
    types = types + ['Category']
    
    types = types + ['Category'] #title
    #types = types + ['Continuous']#WCTitle
    #types = types + ['Continuous']#RatioTitle
    
    #types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
        if MPs == []: continue
        
        lecture = week + 1
        titles = titleList[week]
        
        titledict = {}
        newTitles = []
        for title in titles:
            unigrams = NLTKWrapper.wordtokenizer(title)
            title = ' '.join(unigrams)
            newTitles.append(title.lower())
            for word in unigrams:
                titledict[word.lower()] = True
                
        titles = newTitles
        
        for MP, score in MPs:
            row = []
            
            unigrams = NLTKWrapper.wordtokenizer(MP)
            MP = ' '.join(unigrams)
            
            N = len(MP.split())
            
            hasContentWord = False
            for word in unigrams:
                if word.lower() in contentwords:
                    hasContentWord = True
                    break
            
            OrgAssign = False
            for word in unigrams:
                if word.lower() in orgnizationwords:
                    OrgAssign = True
                    break
            
            titleRepeat = False
            if len(MP) > 0:
                for title in titles:
                    try:
                        if title.find(MP.lower()) != -1:
                            titleRepeat = True
                            break
                    except UnicodeDecodeError:
                        pass
            
            titleCount = 0
            if len(MP) > 0:
                for word in unigrams:
                    if word.lower() in titledict:
                        titleCount = titleCount + 1
                        
            #row.append(MP) #unigram
            #row.append(N)  #
            row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
            row.append(titleRepeat)
            #row.append(titleCount)
            #row.append(titleCount / float(N) if N > 0 else 0)
            
            #row.append(probs[i])
            row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            if score == 'a': continue
            data.append(row)
       
    return head, types, data
        
def getDistributionofRubic(excelfile, prob, titledir, output):
    head, types, data = getBinaryFeatures(excelfile, prob, titledir, output)
    
    class_index = head.index(class_label)
    
    features = [head.index(key) for key in head if key != class_label]
    
    labels = set([row[class_index] for row in data])
    
    totalN = defaultdict(int)
    dict = {}
    for label in labels:
        dict[label] = defaultdict(int)
    
    for row in data:
        label = row[class_index]
        totalN[label] += 1
        
        for f in features:
            if row[f]:
                dict[label][f] += 1
    
    new_head = [class_label]
    new_head += ['totalN']
    new_head += [head[i] for i in features]
    
    new_body = []
    for label in labels:
        row = []
        row.append(label)
        row.append(totalN[label])
        
        for f in features:
            row.append(dict[label][f])
        new_body.append(row)
    
    fio.WriteMatrix(output, new_body, new_head)


def WriteQuality2Weka_Binary(excelfile, prob, titledir, output):#feature are inspired from decision tree
    head, types, data = getBinaryFeatures(excelfile, prob, titledir, output)
    fio.ArffWriter(output, head, types, "Quality", data)
        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    speciteller_datadir = "../data/speciteller/"
    prob = "../data/MP.prob"
    titledir = "E:/Dropbox/reflection project_LRDC/250 Sp11 CLIC All Lecs .2G/titles/"
    
#     wekafile = "../data/weka/quality_binary_model.arff"
#     WriteQuality2Weka_Binary(excelfile, prob, titledir, wekafile)
    
    output = "../data/weka/quality_rubric_distribution.txt"
    getDistributionofRubic(excelfile, prob, titledir, output)