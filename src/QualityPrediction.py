import Survey, fio
from OrigReader import prData
import sys
import NLTKWrapper

topicDict = {2:1,3:1,
             4:2,5:2,6:2,7:2,
             8:3,9:3,
             10:4,11:4,
             12:5,13:5,14:5,15:5,16:5,
             17:6,18:6,19:6,
             20:7,21:7,22:7,
             23:8,24:8,
             }

#Write Quality to Weka
def getQualitywithLecture(excelfile, sheets=range(0,25)):
    Data = []
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        MPs = Survey.getMPQualityPoint(orig)
        if len(MPs) == 0:
            print week
        
        Data.append(MPs)
    
    return Data

def getQuality(excelfile):
    Data = []
    
    sheets = range(0,25)
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        MPs = Survey.getMPQualityPoint(orig)
        if len(MPs) == 0:
            print week
        
        Data = Data + MPs
    
    return Data

def getQualityDistribution(excelfile, output):
    MPs = getQualitywithLecture(excelfile)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    dict = {}
    for i, MPs in enumerate(MPLectures):
        for MP, score in MPs:
            if score not in dict:
                dict[score] = 0
            dict[score] = dict[score] + 1
    
    fio.SaveDict(dict, output, SortbyValueflag = False)

def getQualityLengthDistribution(excelfile):
    MPs = getQualitywithLecture(excelfile)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    all = []
    dict = {}
    for i, MPs in enumerate(MPLectures):
        for MP, score in MPs:
            if score not in dict:
                dict[score] = []
            dict[score].append(len(MP.split()))
            all.append(len(MP.split()))
    
    import numpy
    for key in sorted(dict.keys()):
        print key, "\t", len(dict[key]), '\t', numpy.min(dict[key]), "\t", numpy.max(dict[key]), "\t", numpy.median(dict[key]), "\t", numpy.average(dict[key]), "\t", numpy.std(dict[key]) 
    print "All", "\t", len(all), '\t', numpy.min(all), "\t", numpy.max(all), "\t", numpy.median(all), "\t", numpy.average(all), "\t", numpy.std(all)
    
def getQualityText(excelfile, outputdir, sheets=range(0,25)):
    MPLectures = getQualitywithLecture(excelfile, sheets)
    
    for i, MPs in enumerate(MPLectures):
        week = i + 1
        Text = []
        for MP, _ in MPs:
            MP = ' '.join(NLTKWrapper.wordtokenizer(MP))
            Text.append(MP)
        
        path = outputdir + str(week) + "/"
        fio.NewPath(path)
        filename = path + "MP.txt"
        fio.SaveList(Text, filename)
    
def PostProcessProb(excelfile, datadir, sheets=range(0,25)):
    MPLectures = getQualitywithLecture(excelfile, sheets)
    
    for i, MPs in enumerate(MPLectures):
        week = i + 1
        
        path = datadir + str(week) + "/"
        filename = path + "MP.raw.prob"
        if not fio.IsExist(filename):
            continue
        
        probs = [line.strip() for line in fio.ReadFile(filename)]
    
        k = 0
        P = []
        for MP, _ in MPs:
            MP = ' '.join(NLTKWrapper.wordtokenizer(MP))
            if len(MP.strip()) == 0: 
                P.append("0")
                continue
            
            P.append(probs[k])
            k = k + 1
        
        assert(len(P) == len(MPs))
        filename = path + "MP.prob"    
        fio.SaveList(P, filename)

def getMPProb(lecture, datadir):
    path = datadir + str(lecture) + "/"
    filename = path + "MP.prob"
    if not fio.IsExist(filename):
        return []
        
    probs = [float(line.strip()) for line in fio.ReadFile(filename)]
    return probs
            
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
        
        if score == 'a': continue
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
        
        if score == 'a': continue
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
        
        if score == 'a': continue
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
        
        if score == 'a': continue
        data.append(row)
   
    fio.ArffWriter(output, head, types, "Quality", data)

def WriteQuality2Weka_WC_Unigam(excelfile, prob, output):
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    MPs = getQuality(excelfile)
    
    head = []
    head = head + ['Text']
    head = head + ['WC']
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous']
    types = types + ['Category']
    
    data = []
    for i, (MP, score) in enumerate(MPs):
        row = []
        
        MP = ' '.join(NLTKWrapper.wordtokenizer(MP))
        N = len(MP.split())
        
        row.append(MP)
        row.append(N)
        row.append(score)
        
        if score == 'a': continue
        data.append(row)
   
    fio.ArffWriter(output, head, types, "Quality", data)



def WriteQuality2Weka_WC_Unigam_NonZero(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    head = head + ['Text']
    head = head + ['WC']
    head = head + ['NoneZero'] #length > 0?
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous']
    types = types + ['Category']    #length > 0?
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
            
            row.append(MP)
            row.append(N)            
            row.append(N > 0)
            
            row.append(score)
            i = i + 1
            
            if score == 'a': continue
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
        
def WriteQuality2Weka_WC_Unigam_Content(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    head = head + ['Text']
    head = head + ['WC']
    head = head + ['Content']
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous']
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
            
            row.append(MP)
            row.append(N)            
            row.append(hasContentWord)
            row.append(score)
            i = i + 1
            
            if score == 'a': continue
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
        
def WriteQuality2Weka_WC_Unigam_OrgAssign(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    head = head + ['Text']
    head = head + ['WC']
    head = head + ['OrgAssign']
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous']
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
            
            row.append(MP)
            row.append(N)            
            row.append(OrgAssign)
            row.append(score)
            i = i + 1
            
            if score == 'a': continue
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)

def WriteQuality2Weka_WC_Unigam_Speciteller(excelfile, speciteller_datadir, wekafile):
    head = []
    head = head + ['Text']
    head = head + ['WC']
    head = head + ['ProbBinary']
    head = head + ['Prob']
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Continuous']
    types = types + ['Category']
    
    data = []
    
    MPLectures = getQualitywithLecture(excelfile)
    
    for i, MPs in enumerate(MPLectures):
        week = i + 1
        probs = getMPProb(week, speciteller_datadir)
        
        if MPs == []: continue
        
        for k, (MP, score) in enumerate(MPs):
            row = []
            
            MP = ' '.join(NLTKWrapper.wordtokenizer(MP))
            N = len(MP.split())
            
            row.append(MP)
            row.append(N)
            row.append('True' if probs[k] >= 0.5 else 'False')
            row.append(probs[k])
            row.append(score)
            
            if score == 'a': continue
            data.append(row)
   
    fio.ArffWriter(wekafile, head, types, "Quality", data)
        
def WriteQuality2Weka_WC_Unigam_Title(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    head = []
    head = head + ['Text']
    head = head + ['WC']
    head = head + ['Title']
    head = head + ['WCTitle']
    head = head + ['RatioTitle']
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous']
    types = types + ['Category'] #title
    types = types + ['Continuous']#WCTitle
    types = types + ['Continuous']#RatioTitle
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
            
            row.append(MP)
            row.append(N)            
            row.append(titleRepeat)
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            row.append(score)
            i = i + 1
            
            if score == 'a': continue
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
            
            if score == 'a': continue
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
            
            if score == 'a': continue
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)

def WriteQuality2Weka_New(excelfile, prob, titledir, output):#feature are inspired from decision tree
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
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[i])
            row.append(probs[i] >= 0.5)
            row.append(score)
            i = i + 1
            
            if score == 'a': continue
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)

def WriteQuality2Weka_New_Title(excelfile, speciteller_datadir, titledir, output, sheets=range(0,25)):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile, sheets)
    
    head = []
    #head = head + ['Text'] #ngram
    #head = head + ['WC'] #word count
    head = head + ['NoneZero'] #length > 0?
    head = head + ['Content']
    head = head + ['OrgAssign']
#     head = head + ['Title']
#     head = head + ['WCTitle']
#     head = head + ['RatioTitle']

    head = head + ['Prob'] #Specific
    head = head + ['ProbBinary']
    
    head = head + ['@class@']
    
    types = []
    #types = types + ['String']
    #types = types + ['Continuous'] #word count
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
        if MPs == []: continue
        
        lecture = week + 1
        titles = titleList[week]
        
        probs = getMPProb(lecture, speciteller_datadir)
        
        titledict = {}
        newTitles = []
        for title in titles:
            unigrams = NLTKWrapper.wordtokenizer(title)
            title = ' '.join(unigrams)
            newTitles.append(title.lower())
            for word in unigrams:
                titledict[word.lower()] = True
                
        titles = newTitles
        
        for k, (MP, score) in enumerate(MPs):
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
            
#             row.append(titleRepeat)
#             row.append(titleCount)
#             row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[k])
            row.append(probs[k] >= 0.5)
            row.append(score)
            
            if score == 'a': continue
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
            
            if score == 'a': continue
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
            
            if score == 'a': continue
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
            
            if score == 'a': continue
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
            
            if score == 'a': continue
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
   
def WriteQuality2Weka_DT_Title(excelfile, speciteller_datadir, titledir, output, sheets=range(0,25)):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    #probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile, sheets)
    
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
        
        probs = getMPProb(lecture, speciteller_datadir)
        
        for k, (MP, score) in enumerate(MPs):
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
            
            row.append(probs[k])
            row.append(probs[k] >= 0.5)
            row.append(score)
            
            if score == 'a': continue
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
        
def WriteQuality2Weka_DT_WC_Unigram_Title(excelfile, speciteller_datadir, titledir, output, sheets=range(0,25)):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    #probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile, sheets)
    
    head = []
    #head = head + ['Text'] #ngram
    #head = head + ['WC'] #word count
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
    #types = types + ['Continuous'] #word count
    types = types + ['Category']    #length > 0?
    types = types + ['Category']
    types = types + ['Category']
    
#     types = types + ['Category'] #title
#     types = types + ['Continuous']#WCTitle
#     types = types + ['Continuous']#RatioTitle
    
    types = types + ['Continuous']
    types = types + ['Category']
    types = types + ['Category']
    
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
        
        probs = getMPProb(lecture, speciteller_datadir)
        
        for k, (MP, score) in enumerate(MPs):
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
            
#             row.append(titleRepeat)
#             row.append(titleCount)
#             row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[k])
            row.append(probs[k] >= 0.5)
            row.append(score)
            
            if score == 'a': continue
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
        
def WriteQuality2Weka_WC_Unigram_Title(excelfile, speciteller_datadir, titledir, output, sheets=range(0,25)):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    #probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile, sheets)
    
    head = []
    head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']
    
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
        
        probs = getMPProb(lecture, speciteller_datadir)
        
        for k, (MP, score) in enumerate(MPs):
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
            row.append(score)
            
            if score == 'a': continue
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
            
            if score == 'a': continue
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
            
            if score == 'a': continue
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
            
            if score == 'a': continue
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
            
            if score == 'a': continue
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
            
            if score == 'a': continue
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
            
            if score == 'a': continue
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
            
            if score == 'a': continue
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
            if len(MPs) == 0: continue
            
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
                
                if score == 'a': continue
                if week == fold:
                    test.append(row)
                else:
                    data.append(row)
            
            outputfile = output + "_" + str(fold) + "_train.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", data)
            
            outputfile = output + "_" + str(fold) + "_test.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", test)

def WriteQuality2Weka_CrossLecture_New(excelfile, prob, titledir, output):#feature are inspired from decision tree
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
    
    for fold in range(len(MPLectures)):
        i = 0
        data = []
        test = []
        for week, MPs in enumerate(MPLectures):
            if len(MPs) == 0: continue
            
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
                
                if score == 'a': continue
                if week == fold:
                    test.append(row)
                else:
                    data.append(row)
            
            outputfile = output + "_" + str(fold) + "_train.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", data)
            
            outputfile = output + "_" + str(fold) + "_test.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", test)
             
def WriteQuality2Weka_CrossLecture_WC_Unigram(excelfile, prob, titledir, output):#feature are inspired from decision tree
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
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']
    
    for fold in range(len(MPLectures)):
        i = 0
        data = []
        test = []
        for week, MPs in enumerate(MPLectures):
            if len(MPs) == 0: continue
            
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
                row.append(score)
                i = i + 1
                
                if score == 'a': continue
                if week == fold:
                    test.append(row)
                else:
                    data.append(row)
            
            outputfile = output + "_" + str(fold) + "_train.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", data)
            
            outputfile = output + "_" + str(fold) + "_test.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", test)

def WriteQuality2Weka_CrossTopic_DT(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    topics = sorted(set(topicDict.values()))
    
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
    
    for fold in topics:
        i = 0
        data = []
        test = []
        for week, MPs in enumerate(MPLectures):
            if len(MPs) == 0: continue
            
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
                
                if score == 'a': continue
                if topicDict[lecture] == fold:
                    test.append(row)
                else:
                    data.append(row)
            
            outputfile = output + "_" + str(fold) + "_train.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", data)
            
            outputfile = output + "_" + str(fold) + "_test.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", test)

def WriteQuality2Weka_CrossTopic_New(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    topics = sorted(set(topicDict.values()))
    
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
    
    for fold in topics:
        i = 0
        data = []
        test = []
        for week, MPs in enumerate(MPLectures):
            if len(MPs) == 0: continue
            
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
                
                if score == 'a': continue
                if topicDict[lecture] == fold:
                    test.append(row)
                else:
                    data.append(row)
            
            outputfile = output + "_" + str(fold) + "_train.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", data)
            
            outputfile = output + "_" + str(fold) + "_test.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", test)
            
def WriteQuality2Weka_CrossTopic_MC_Unigram(excelfile, prob, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile)
    
    topics = sorted(set(topicDict.values()))
    
    head = []
    head = head + ['Text'] #ngram
    head = head + ['WC'] #word count 
    head = head + ['@class@']
    
    types = []
    types = types + ['String']
    types = types + ['Continuous'] #word count
    types = types + ['Category']
    
    for fold in topics:
        i = 0
        data = []
        test = []
        for week, MPs in enumerate(MPLectures):
            if len(MPs) == 0: continue
            
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
                row.append(score)
                i = i + 1
                
                if score == 'a': continue
                if topicDict[lecture] == fold:
                    test.append(row)
                else:
                    data.append(row)
            
            outputfile = output + "_" + str(fold) + "_train.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", data)
            
            outputfile = output + "_" + str(fold) + "_test.arff"
            fio.ArffWriter(outputfile, head, types, "Quality", test)

def formatTestlabel(input, output, sheets=range(0,4)):
    head, body = fio.ReadMatrix(input, hasHead=True)
    
    testlabels = [row[1] for row in body]
    
    N = len(sheets)
    
    n = len(testlabels)/N
    
    formatlabels = []
    
    for i in range(N):
        labels = testlabels[n*i:n*(i+1)]
        formatlabels.append(labels)
    
    newbody = []
    for i in range(n):
        row = []
        for j in range(N):
            row.append(float(formatlabels[j][i]))
        row.append(sum(row))
        newbody.append(row)

    fio.WriteMatrix(output, newbody, header=None)
        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
  
    getQualityLengthDistribution(excelfile)
    exit(0)
    
    #dis = "../data/q_dis.txt"
    #getQualityDistribution(excelfile, dis)
    
    speciteller_datadir = "../data/speciteller/"
    #getQualityText(excelfile, datadir)
    
    prob = "../data/MP.prob"
    #PostProcessProb(excelfile, speciteller_datadir)
    titledir = "E:/Dropbox/reflection project_LRDC/250 Sp11 CLIC All Lecs .2G/titles/"
    
#     wekafile = "../data/weka/quality_DT.arff"
#     WriteQuality2Weka_DT(excelfile, prob, titledir, wekafile)
#          
#     wekafile = "../data/weka/quality_WC_Unigram.arff"
#     WriteQuality2Weka_WC_Unigam(excelfile, prob, wekafile)
#  
#     wekafile = "../data/weka/quality_WC_Unigam_NonZero.arff"
#     WriteQuality2Weka_WC_Unigam_NonZero(excelfile, prob, titledir, wekafile)
#       
#     wekafile = "../data/weka/quality_WC_Unigam_Content.arff"
#     WriteQuality2Weka_WC_Unigam_Content(excelfile, prob, titledir, wekafile)
#       
#     wekafile = "../data/weka/quality_WC_Unigam_OrgAssign.arff"
#     WriteQuality2Weka_WC_Unigam_OrgAssign(excelfile, prob, titledir, wekafile)
#       
#     wekafile = "../data/weka/quality_WC_Unigam_Speciteller.arff"
#     WriteQuality2Weka_WC_Unigam_Speciteller(excelfile, speciteller_datadir, wekafile)
#       
#     wekafile = "../data/weka/quality_WC_Unigam_Title.arff"
#     WriteQuality2Weka_WC_Unigam_Title(excelfile, prob, titledir, wekafile)
#       
#     wekafile = "../data/weka/quality_CrossLecture_DT"
#     WriteQuality2Weka_CrossLecture_DT(excelfile, prob, titledir, wekafile)
#        
#     wekafile = "../data/weka/quality_CrossLecture_WC_Unigram"
#     WriteQuality2Weka_CrossLecture_WC_Unigram(excelfile, prob, titledir, wekafile)
#      
#     wekafile = "../data/weka/quality_CrossTopic_DT"
#     WriteQuality2Weka_CrossTopic_DT(excelfile, prob, titledir, wekafile)
#     
#     wekafile = "../data/weka/quality_CrossTopic_WC_Unigram"
#     WriteQuality2Weka_CrossTopic_MC_Unigram(excelfile, prob, titledir, wekafile)
#
    
    excelfile_2010 = "../data/2010Spring.xls"
    speciteller_datadir_2010 = "../data/speciteller_2010/"
    #getQualityText(excelfile_2010, speciteller_datadir_2010, sheets=range(0,4))
    
    #PostProcessProb(excelfile_2010, speciteller_datadir_2010, sheets=range(0,4))
    
    #cross course begin
#     wekafile = "../data/weka/quality_CrossCourse_DT_train.arff"
#     WriteQuality2Weka_DT_Title(excelfile, speciteller_datadir, titledir, wekafile)
#        
#     wekafile = "../data/weka/quality_CrossCourse_DT_test.arff"
#     WriteQuality2Weka_DT_Title(excelfile_2010, speciteller_datadir_2010, titledir, wekafile, sheets=range(0,4))
#                
#     wekafile = "../data/weka/quality_CrossCourse_WC_Unigram_train.arff"
#     WriteQuality2Weka_WC_Unigram_Title(excelfile, speciteller_datadir, titledir, wekafile)
#        
#     wekafile = "../data/weka/quality_CrossCourse_WC_Unigram_test.arff"
#     WriteQuality2Weka_WC_Unigram_Title(excelfile_2010, speciteller_datadir_2010, titledir, wekafile, sheets=range(0,4))
#      
#     wekafile = "../data/weka/quality_CrossCourse_New_train.arff"
#     WriteQuality2Weka_New_Title(excelfile, speciteller_datadir, titledir, wekafile)
#       
#     wekafile = "../data/weka/quality_CrossCourse_New_test.arff"
#     WriteQuality2Weka_New_Title(excelfile_2010, speciteller_datadir_2010, titledir, wekafile, sheets=range(0,4))
    #cross course end
    
#     wekafile = "../data/weka/quality_New.arff"
#     WriteQuality2Weka_New(excelfile, prob, titledir, wekafile)
#    
#     wekafile = "../data/weka/quality_CrossLecture_New"
#     WriteQuality2Weka_CrossLecture_New(excelfile, prob, titledir, wekafile)
#      
#     wekafile = "../data/weka/quality_CrossTopic_New"
#     WriteQuality2Weka_CrossTopic_New(excelfile, prob, titledir, wekafile)
#     

    #fio.ExtractWekaScore("../../QualityPrediction/log.txt", "../data/weka/quality_2.txt")
    
#     for label in ["../data/weka/quality_CrossCourse_New_test.label",
#                   "../data/weka/quality_CrossCourse_DT_test.label",
#                   "../data/weka/quality_CrossCourse_WC_Unigram_test.label"
#                   ]:
#           
#         formatTestlabel(label, label + ".new")

    print "done"
