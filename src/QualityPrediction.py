import Survey, fio
from OrigReader import prData
import sys
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

def getQualitywithLecture(excelfile):
    Data = []
    
    sheets = range(1,24)
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        MPs = Survey.getMPQualityPoint(orig)
        if len(MPs) == 0:
            print week
        
        Data.append(MPs)
    
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
    
    probs = [line.strip() for line in fio.ReadFile(prob)]
    
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
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
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
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
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
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
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

def WriteQuality2Weka_DT(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    head = head + ['OrgAssign']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    types = types + ['Category']
    types = types + ['Category']
    
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
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
                        
            row.append(MP) #unigram
            row.append(N)  #
            row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
            row.append(titleRepeat)
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[i])
            row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
        
def WriteQuality2Weka_ALL(excelfile, prob, output):
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
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

def WriteQuality2Weka_DT_WC(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    head = head + ['Text'] #ngram
    #head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    head = head + ['OrgAssign']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    #types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    types = types + ['Category']
    types = types + ['Category']
    
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
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
                        
            row.append(MP) #unigram
            #row.append(N)  #
            row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
            row.append(titleRepeat)
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[i])
            row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
   
def WriteQuality2Weka_DT_Ngram(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    #head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    head = head + ['OrgAssign']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    #types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    types = types + ['Category']
    types = types + ['Category']
    
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
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
            row.append(N)  #
            row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
            row.append(titleRepeat)
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[i])
            row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
   
def WriteQuality2Weka_DT_NoneZero(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    #head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    head = head + ['OrgAssign']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous'] #word count
    #types = types + ['Category']    #length > 0?
    types = types + ['Category']
    types = types + ['Category']
    
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
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
                        
            row.append(MP) #unigram
            row.append(N)  #
            #row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
            row.append(titleRepeat)
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[i])
            row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
   
def WriteQuality2Weka_DT_Content(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    #head = head + ['Content']
    head = head + ['OrgAssign']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    #types = types + ['Category']
    types = types + ['Category']
    
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
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
                        
            row.append(MP) #unigram
            row.append(N)  #
            row.append(N > 0)
            
            #row.append(hasContentWord)
            row.append(OrgAssign)
            
            row.append(titleRepeat)
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[i])
            row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
   
def WriteQuality2Weka_DT_OrgAssign(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    #head = head + ['OrgAssign']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    types = types + ['Category']
    #types = types + ['Category']
    
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
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
                        
            row.append(MP) #unigram
            row.append(N)  #
            row.append(N > 0)
            
            row.append(hasContentWord)
            #row.append(OrgAssign)
            
            row.append(titleRepeat)
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[i])
            row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
   
def WriteQuality2Weka_DT_Title(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    head = head + ['OrgAssign']
    #head = head + ['Title']
    #head = head + ['WCTitle']
    #head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    types = types + ['Category']
    types = types + ['Category']
    
#     types = types + ['Category'] #title
#     types = types + ['Continuous']#WCTitle
#     types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
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
                        
            row.append(MP) #unigram
            row.append(N)  #
            row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
#             row.append(titleRepeat)
#             row.append(titleCount)
#             row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[i])
            row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
   
def WriteQuality2Weka_DT_Specific(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    head = head + ['OrgAssign']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']

#     head = head + ['Prob'] #Specific
#     head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    types = types + ['Category']
    types = types + ['Category']
    
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
    
#     types = types + ['Continuous']
#     types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
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
                        
            row.append(MP) #unigram
            row.append(N)  #
            row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
            row.append(titleRepeat)
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
#             row.append(probs[i])
#             row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)

def WriteQuality2Weka_DT_Ngram_WC(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    #head = head + ['Text'] #ngram
    #head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    head = head + ['OrgAssign']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    #types = types + ['String']
    #types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    types = types + ['Category']
    types = types + ['Category']
    
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
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
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[i])
            row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
   
def WriteQuality2Weka_DT_Ngram_NoneZero(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    #head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    #head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    head = head + ['OrgAssign']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    #types = types + ['String']
    types = types + ['Continuous'] #word count
    #types = types + ['Category']    #length > 0?
    types = types + ['Category']
    types = types + ['Category']
    
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
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
            row.append(N)  #
            #row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
            row.append(titleRepeat)
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[i])
            row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
   
def WriteQuality2Weka_DT_Ngram_Content(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    #head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    #head = head + ['Content']
    head = head + ['OrgAssign']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    #types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    #types = types + ['Category']
    types = types + ['Category']
    
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
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
            row.append(N)  #
            row.append(N > 0)
            
            #row.append(hasContentWord)
            row.append(OrgAssign)
            
            row.append(titleRepeat)
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[i])
            row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
   
def WriteQuality2Weka_DT_Ngram_OrgAssign(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    #head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    #head = head + ['OrgAssign']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    #types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    types = types + ['Category']
    #types = types + ['Category']
    
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
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
            row.append(N)  #
            row.append(N > 0)
            
            row.append(hasContentWord)
            #row.append(OrgAssign)
            
            row.append(titleRepeat)
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[i])
            row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
   
def WriteQuality2Weka_DT_Ngram_Title(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    #head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    head = head + ['OrgAssign']
    #head = head + ['Title']
    #head = head + ['WCTitle']
    #head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    #types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    types = types + ['Category']
    types = types + ['Category']
    
#     types = types + ['Category'] #title
#     types = types + ['Continuous']#WCTitle
#     types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
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
            row.append(N)  #
            row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
#             row.append(titleRepeat)
#             row.append(titleCount)
#             row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[i])
            row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
   
def WriteQuality2Weka_DT_Ngram_Specific(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    #head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    head = head + ['OrgAssign']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']

#     head = head + ['Prob'] #Specific
#     head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    #types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    types = types + ['Category']
    types = types + ['Category']
    
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
    
#     types = types + ['Continuous']
#     types = types + ['Category']
    types = types + ['Category']
    
    i = 0
    data = []
    for week, MPs in enumerate(MPLectures):
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
            row.append(N)  #
            row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
            row.append(titleRepeat)
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
#             row.append(probs[i])
#             row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)

def WriteQuality2Weka_CrossLecture_DT(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    head = head + ['OrgAssign']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    types = types + ['Category']
    types = types + ['Category']
    
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    for fold in range(len(MPLectures)):
        i = 0
        data = []
        test = []
        for week, MPs in enumerate(MPLectures):
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
                            
                row.append(MP) #unigram
                row.append(N)  #
                row.append(N > 0)
                
                row.append(hasContentWord)
                row.append(OrgAssign)
                
                row.append(titleRepeat)
                row.append(titleCount)
                row.append(titleCount / float(N) if N > 0 else 0)
                
                row.append(probs[i])
                row.append(probs[i] >= 0.5)
                row.append(score)
                i = i + 1
                
                if week == fold:
                    test.append(row)
                else:
                    data.append(row)
            
            outputfile = output + "_" + str(fold) + "_train.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", data)
            
            outputfile = output + "_" + str(fold) + "_test.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", test)
 
def WriteQuality2Weka_CrossLecture_DT_Unigram(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    #head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    head = head + ['OrgAssign']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    #types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    types = types + ['Category']
    types = types + ['Category']
    
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
    for fold in range(len(MPLectures)):
        i = 0
        data = []
        test = []
        for week, MPs in enumerate(MPLectures):
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
                row.append(N)  #
                row.append(N > 0)
                
                row.append(hasContentWord)
                row.append(OrgAssign)
                
                row.append(titleRepeat)
                row.append(titleCount)
                row.append(titleCount / float(N) if N > 0 else 0)
                
                row.append(probs[i])
                row.append(probs[i] >= 0.5)
                row.append(score)
                i = i + 1
                
                if week == fold:
                    test.append(row)
                else:
                    data.append(row)
            
            outputfile = output + "_" + str(fold) + "_train.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", data)
            
            outputfile = output + "_" + str(fold) + "_test.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", test)
                
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
#     wekafile = "../data/quality_unigram.arff"
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
# 
#     wekafile = "../data/quality_wc_unigram.arff"
#     WriteQuality2Weka_WC_Ngram(excelfile, prob, wekafile)
    
    titledir = "E:/Dropbox/reflection project_LRDC/250 Sp11 CLIC All Lecs .2G/titles/"
    
#     wekafile = "../data/quality_DT.arff"
#     WriteQuality2Weka_DT(excelfile, prob, titledir, wekafile)
#      
#     wekafile = "../data/quality_DT_WC.arff"
#     WriteQuality2Weka_DT_WC(excelfile, prob, titledir, wekafile)
#      
#     wekafile = "../data/quality_DT_Ngram.arff"
#     WriteQuality2Weka_DT_Ngram(excelfile, prob, titledir, wekafile)
#      
#     wekafile = "../data/quality_DT_NoneZero.arff"
#     WriteQuality2Weka_DT_NoneZero(excelfile, prob, titledir, wekafile)
#      
#     wekafile = "../data/quality_DT_Content.arff"
#     WriteQuality2Weka_DT_Content(excelfile, prob, titledir, wekafile)
#      
#     wekafile = "../data/quality_DT_OrgAssign.arff"
#     WriteQuality2Weka_DT_OrgAssign(excelfile, prob, titledir, wekafile)
#      
#     wekafile = "../data/quality_DT_Specific.arff"
#     WriteQuality2Weka_DT_Specific(excelfile, prob, titledir, wekafile)
#      
#     wekafile = "../data/quality_DT_Title.arff"
#     WriteQuality2Weka_DT_Title(excelfile, prob, titledir, wekafile)
    
#     wekafile = "../data/quality_DT_Ngram_WC.arff"
#     WriteQuality2Weka_DT_Ngram_WC(excelfile, prob, titledir, wekafile)
#     
#     wekafile = "../data/quality_DT_Ngram_NoneZero.arff"
#     WriteQuality2Weka_DT_Ngram_NoneZero(excelfile, prob, titledir, wekafile)
#       
#     wekafile = "../data/quality_DT_Ngram_Content.arff"
#     WriteQuality2Weka_DT_Ngram_Content(excelfile, prob, titledir, wekafile)
#       
#     wekafile = "../data/quality_DT_Ngram_OrgAssign.arff"
#     WriteQuality2Weka_DT_Ngram_OrgAssign(excelfile, prob, titledir, wekafile)
#       
#     wekafile = "../data/quality_DT_Ngram_Specific.arff"
#     WriteQuality2Weka_DT_Ngram_Specific(excelfile, prob, titledir, wekafile)
#       
#     wekafile = "../data/quality_DT_Ngram_Title.arff"
#     WriteQuality2Weka_DT_Ngram_Title(excelfile, prob, titledir, wekafile)
    
#     wekafile = "../data/quality_DT"
#     WriteQuality2Weka_CrossLecture_DT(excelfile, prob, titledir, wekafile)
#     
#     wekafile = "../data/quality_DT_Unigram"
#     WriteQuality2Weka_CrossLecture_DT_Unigram(excelfile, prob, titledir, wekafile)
    
    fio.ExtractWekaScore("../../QualityPrediction/log.txt", "../data/quality_DT_Ngram_CrossLecture.txt")
    
    print "done"
