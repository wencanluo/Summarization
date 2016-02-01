import Survey, fio
from OrigReader import prData
import sys
import NLTKWrapper
import numpy
import random

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
def getQualitywithLecture(excelfile, sheets=range(0,25), filters=None):
    Data = []
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        MPs = Survey.getMPQualityPoint(orig, filters=filters)
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

def getQualityLengthDistribution(excelfile, sheets=range(0,25), filters=None):
    MPLectures = getQualitywithLecture(excelfile, sheets=sheets, filters=filters)
    
    emptycount = 0
    all = []
    dict = {}
    for i, MPs in enumerate(MPLectures):
        for MP, score in MPs:
            if score == 'a': continue
            
            if score not in dict:
                dict[score] = []
            
            N = len(MP.split())
            dict[score].append(N)
            
            if N==0:
                emptycount += 1
            
            all.append(len(MP.split()))
    
    import numpy
    for key in sorted(dict.keys()):
        print key, "\t", len(dict[key]), '\t', numpy.min(dict[key]), "\t", numpy.max(dict[key]), "\t", numpy.median(dict[key]), "\t", numpy.average(dict[key]), "\t", numpy.std(dict[key]) 
    print "All", "\t", len(all), '\t', numpy.min(all), "\t", numpy.max(all), "\t", numpy.median(all), "\t", numpy.average(all), "\t", numpy.std(all)
    
    print emptycount, float(emptycount)/len(all)
    
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


def getQualityPredictionCourseMIRROR(excelfile, cid, prediction_resutls):
    Data = getQualitywithLectureCourseMIRROR(excelfile, cid)
    
    true_label, predictions = fio.ReadMatrix(prediction_resutls, hasHead=True)
    
    

def getQualitywithLectureCourseMIRROR(excelfile, cid):
    data = fio.LoadDictJson(excelfile)
    
    MPs = {}
    Users = {}
    
    for ref in data["results"]:
        if ref['cid'] != cid: continue
        
        week = ref['lecture_number']
        
        if week not in MPs:
            MPs[week] = []

        MP = ref['q2']
        MP = MP[:MP.rfind('||')]
        
        MP = ' '.join(NLTKWrapper.wordtokenizer(MP))
        
        score = random.randint(0, 3)
        
        MPs[week].append((MP, str(score)+'.0'))
    
    Data = []
    
    max = numpy.max(MPs.keys())
    for week in range(1, max+1):
        if week not in MPs:
            Text = []
        else:
            Text = MPs[week]
        
        Data.append(Text)
        
    return Data

def getQualityTextCourseMIRROR(excelfile, cid, outputdir):
    data = fio.LoadDictJson(excelfile)
    
    MPs = {}
    Users = {}
    
    for ref in data["results"]:
        if ref['cid'] != cid: continue
        
        week = ref['lecture_number']
        
        if week not in MPs:
            MPs[week] = []
            Users[week] = []
        
        MP = ref['q2']
        MP = MP[:MP.rfind('||')]
        
        MP = ' '.join(NLTKWrapper.wordtokenizer(MP))
        MPs[week].append(MP)
        Users[week].append(ref['user'])
    
    for week in sorted(MPs):
        Text = MPs[week]
        
        path = outputdir + str(week) + "/"
        fio.NewPath(path)
        filename = path + "MP.txt"
        fio.SaveList(Text, filename)
        
        filename = path + "MP.users"
        fio.SaveList(Users[week], filename)
        
            
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
        
    #print filename
    
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
        
def WriteQuality2Weka_DT_WC(excelfile, speciteller_datadir, titledir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    #probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
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

def WriteQuality2Weka_DT(excelfile, speciteller_datadir, titledir, output, sheets=range(0,25), filters=None):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    #probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir, sheets)
    
    MPLectures = getQualitywithLecture(excelfile, sheets=sheets, filters=filters)
    
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
                        
            row.append(MP) #unigram
            row.append(N)  #
            row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
            row.append(titleRepeat)
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[k])
            row.append(probs[k] >= 0.5)
            row.append(score)
            
            if score == 'a': continue
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)

def remove_feature(head, types, data, feature2remove):
    feature = head.index(feature2remove)
    
    head.pop(feature)
    types.pop(feature)
    
    new_body = []
    for row in data:
        if row[feature]:
            row.pop(feature)
            new_body.append(row)
    return head, types, new_body
    
def get_Quality_RubricFeatures(excelfile, speciteller_datadir, titledir, sheets=range(0,25), filters=None):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    #probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir, sheets)
    
    MPLectures = getQualitywithLecture(excelfile, sheets, filters=filters)
    
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
            
            row.append(titleRepeat)
            row.append(titleCount)
            row.append(titleCount / float(N) if N > 0 else 0)
            
            row.append(probs[k])
            row.append(probs[k] >= 0.5)
            row.append(score)
            
            
            if score == 'a': continue
            data.append(row)
       
    return head, types, data
        
def WriteQuality2Weka_New(excelfile, speciteller_datadir, titledir, output, sheets=range(0,25), filters=None):#feature are inspired from decision tree
    head, types, data = get_Quality_RubricFeatures(excelfile, speciteller_datadir, titledir, sheets, filters=filters)
    fio.ArffWriter(output, head, types, "Quality", data)
    
def WriteQuality2Weka_New_Title(excelfile, speciteller_datadir, titledir, output, sheets=range(0,25), filters=None):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile, sheets, filters=filters)
    
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

def WriteQuality2Weka_New_Title_NoneZero(excelfile, speciteller_datadir, titledir, output, sheets=range(0,25), filters=None):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir)
    
    MPLectures = getQualitywithLecture(excelfile, sheets, filters=filters)
    
    head = []
    #head = head + ['Text'] #ngram
    #head = head + ['WC'] #word count
    #head = head + ['NoneZero'] #length > 0?
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
    #types = types + ['Category']    #length > 0?
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
            if N==0: continue
            
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
            #row.append(N > 0)
            
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
            try:
                row.append(probs[k])
            except Exception as e:
                print lecture, len(probs), k
                print e
                
            row.append(probs[k] >= 0.5)
            row.append(score)
            
            if score == 'a': continue
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)

def WriteQuality2Weka_DT_Title_NoneZero(excelfile, speciteller_datadir, titledir, output, sheets=range(0,25)):#feature are inspired from decision tree
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
    #head = head + ['NoneZero'] #length > 0?
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
    #types = types + ['Category']    #length > 0?
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
            
            if N==0: continue
            
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
            
#             row.append(titleRepeat)
#             row.append(titleCount)
#             row.append(titleCount / float(N) if N > 0 else 0)
            try:
                row.append(probs[k])
            except Exception as e:
                print lecture, len(probs), k
                print e
                
            row.append(probs[k] >= 0.5)
            row.append(score)
            
            if score == 'a': continue
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)
        
def WriteQuality2Weka_DT_Title_CourseMIRROR(excelfile, cid, speciteller_datadir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    
    MPLectures = getQualitywithLectureCourseMIRROR(excelfile, cid)
    
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
            
            row.append(MP) #unigram
            row.append(N)  #
            row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
            try:
                row.append(probs[k])
            except Exception as e:
                print lecture
                print MP
                print e
                exit(-1)
                
            row.append(probs[k] >= 0.5)
            row.append(score)
            
            if score == 'a': continue
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)

def WriteQuality2Weka_DT_Title_NoneZero_CourseMIRROR(excelfile, cid, speciteller_datadir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    
    MPLectures = getQualitywithLectureCourseMIRROR(excelfile, cid)
    
    head = []
    head = head + ['Text'] #ngram
    head = head + ['WC'] #word count
    #head = head + ['NoneZero'] #length > 0?
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
    #types = types + ['Category']    #length > 0?
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
            
            row.append(MP) #unigram
            row.append(N)  #
            #row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
            try:
                row.append(probs[k])
            except Exception as e:
                print lecture
                print MP
                print e
                exit(-1)
                
            row.append(probs[k] >= 0.5)
            row.append(score)
            
            if score == 'a': continue
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)

def WriteQuality2Weka_Rubric_Title_CourseMIRROR(excelfile, cid, speciteller_datadir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    
    MPLectures = getQualitywithLectureCourseMIRROR(excelfile, cid)
    
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
            
            #row.append(MP) #unigram
            #row.append(N)  #
            row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
            try:
                row.append(probs[k])
            except Exception as e:
                print lecture
                print MP
                print e
                exit(-1)
                
            row.append(probs[k] >= 0.5)
            row.append(score)
            
            if score == 'a': continue
            data.append(row)
       
        fio.ArffWriter(output, head, types, "Quality", data)

def WriteQuality2Weka_Rubric_Title_NoneZero_CourseMIRROR(excelfile, cid, speciteller_datadir, output):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    
    MPLectures = getQualitywithLectureCourseMIRROR(excelfile, cid)
    
    head = []
    #head = head + ['Text'] #ngram
    #head = head + ['WC'] #word count
    #head = head + ['NoneZero'] #length > 0?
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
    #types = types + ['Category']    #length > 0?
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
            
            #row.append(MP) #unigram
            #row.append(N)  #
            #row.append(N > 0)
            
            row.append(hasContentWord)
            row.append(OrgAssign)
            
            try:
                row.append(probs[k])
            except Exception as e:
                print lecture
                print MP
                print e
                exit(-1)
                
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
        
def WriteQuality2Weka_WC_Unigram_Title(excelfile, speciteller_datadir, titledir, output, sheets=range(0,25), filters=None):#feature are inspired from decision tree
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    #probs = [float(line.strip()) for line in fio.ReadFile(prob)]
    
    contentwords = [line.strip().lower() for line in fio.ReadFile("content.txt")]
    orgnizationwords = [line.strip().lower() for line in fio.ReadFile("organization_assignment.txt")]
    titleList = Survey.getTitles(titledir, sheets)
    
    MPLectures = getQualitywithLecture(excelfile, sheets, filters=filters)
    
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

def WriteQuality2Weka_CrossLecture_New_Title(excelfile, prob, titledir, output):#feature are inspired from decision tree
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
                
#                 row.append(titleRepeat)
#                 row.append(titleCount)
#                 row.append(titleCount / float(N) if N > 0 else 0)
                
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

def WriteQuality2Weka_CrossTopic_New_Title(excelfile, prob, titledir, output):#feature are inspired from decision tree
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
                
#                 row.append(titleRepeat)
#                 row.append(titleCount)
#                 row.append(titleCount / float(N) if N > 0 else 0)
                
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

def TestNewCourse():
    excelfile = "../data/2011Spring.xls"
    speciteller_datadir = "../data/speciteller/"
    titledir = "E:/Dropbox/reflection project_LRDC/250 Sp11 CLIC All Lecs .2G/titles/"

#     wekafile = "../data/weka/quality_CrossCourse_DT_Title.arff"
#     WriteQuality2Weka_DT_Title(excelfile, speciteller_datadir, titledir, wekafile)
#     wekafile = "../data/weka/quality_CrossCourse_DT_Title_NoneZero.arff"
#     WriteQuality2Weka_DT_Title_NoneZero(excelfile, speciteller_datadir, titledir, wekafile)
#     wekafile = "../data/weka/quality_CrossCourse_Rubric_Title.arff"
#     WriteQuality2Weka_New_Title(excelfile, speciteller_datadir, titledir, wekafile)
    
    wekafile = "../data/weka/quality_CrossCourse_Rubric_Title_NoneZero.arff"
    WriteQuality2Weka_New_Title_NoneZero(excelfile, speciteller_datadir, titledir, wekafile)
    
    coursemirrorfile = "../data/CourseMirror/Reflection.json"
    cid = 'IE256'
    speciteller_datadir = "../data/speciteller_IE256/"
    #getQualityTextCourseMIRROR(coursemirrorfile, cid, speciteller_datadir)
    wekafile = "../data/weka/quality_CrossCourse_DT_Title_IE256.arff"
    #WriteQuality2Weka_DT_Title_CourseMIRROR(coursemirrorfile, cid, speciteller_datadir, wekafile)
    
    wekafile = "../data/weka/quality_CrossCourse_DT_Title_NoneZero_IE256.arff"
    #WriteQuality2Weka_DT_Title_NoneZero_CourseMIRROR(coursemirrorfile, cid, speciteller_datadir, wekafile)
    
    wekafile = "../data/weka/quality_CrossCourse_Rubric_Title_IE256.arff"
    #WriteQuality2Weka_Rubric_Title_CourseMIRROR(coursemirrorfile, cid, speciteller_datadir, wekafile)
    
    wekafile = "../data/weka/quality_CrossCourse_Rubric_Title_NoneZero_IE256.arff"
    WriteQuality2Weka_Rubric_Title_NoneZero_CourseMIRROR(coursemirrorfile, cid, speciteller_datadir, wekafile)
    
    cid = 'PHYS0175'
    speciteller_datadir = "../data/speciteller_PHYS0175/"
    #getQualityTextCourseMIRROR(coursemirrorfile, cid, speciteller_datadir)
    wekafile = "../data/weka/quality_CrossCourse_DT_Title_PHYS0175.arff"
    #WriteQuality2Weka_DT_Title_CourseMIRROR(coursemirrorfile, cid, speciteller_datadir, wekafile)

def testH1():
    # H1
    wekafile = "../data/weka/quality_DT.arff"
    WriteQuality2Weka_DT(excelfile, speciteller_datadir, titledir, wekafile)
           
    wekafile = "../data/weka/quality_WC_Unigram.arff"
    WriteQuality2Weka_WC_Unigam(excelfile, prob, wekafile)
   
    wekafile = "../data/weka/quality_WC_Unigam_NonZero.arff"
    WriteQuality2Weka_WC_Unigam_NonZero(excelfile, prob, titledir, wekafile)
        
    wekafile = "../data/weka/quality_WC_Unigam_Content.arff"
    WriteQuality2Weka_WC_Unigam_Content(excelfile, prob, titledir, wekafile)
        
    wekafile = "../data/weka/quality_WC_Unigam_OrgAssign.arff"
    WriteQuality2Weka_WC_Unigam_OrgAssign(excelfile, prob, titledir, wekafile)
        
    wekafile = "../data/weka/quality_WC_Unigam_Speciteller.arff"
    WriteQuality2Weka_WC_Unigam_Speciteller(excelfile, speciteller_datadir, wekafile)
        
    wekafile = "../data/weka/quality_WC_Unigam_Title.arff"
    WriteQuality2Weka_WC_Unigam_Title(excelfile, prob, titledir, wekafile)
        
def testH2():
    #     #H2.a
    wekafile = "../data/weka/quality_CrossLecture_DT"
    WriteQuality2Weka_CrossLecture_DT(excelfile, prob, titledir, wekafile)
         
    wekafile = "../data/weka/quality_CrossLecture_WC_Unigram"
    WriteQuality2Weka_CrossLecture_WC_Unigram(excelfile, prob, titledir, wekafile)
     
    wekafile = "../data/weka/quality_CrossLecture_New"
    WriteQuality2Weka_CrossLecture_New(excelfile, prob, titledir, wekafile)
     
    #H2.b
    wekafile = "../data/weka/quality_CrossTopic_DT"
    WriteQuality2Weka_CrossTopic_DT(excelfile, prob, titledir, wekafile)
      
    wekafile = "../data/weka/quality_CrossTopic_WC_Unigram"
    WriteQuality2Weka_CrossTopic_MC_Unigram(excelfile, prob, titledir, wekafile)
     
    wekafile = "../data/weka/quality_CrossTopic_New"
    WriteQuality2Weka_CrossTopic_New(excelfile, prob, titledir, wekafile)

def testH2c():
    wekafile = "../data/weka/quality_CrossCourse_DT_train.arff"
    WriteQuality2Weka_DT(excelfile, speciteller_datadir, titledir, wekafile)
            
    wekafile = "../data/weka/quality_CrossCourse_DT_test.arff"
    WriteQuality2Weka_DT(excelfile_2010, speciteller_datadir_2010, titledir_2010, wekafile, sheets=range(0,4), filters=filters)
                    
    wekafile = "../data/weka/quality_CrossCourse_WC_Unigram_train.arff"
    WriteQuality2Weka_WC_Unigram_Title(excelfile, speciteller_datadir, titledir, wekafile)
            
    wekafile = "../data/weka/quality_CrossCourse_WC_Unigram_test.arff"
    WriteQuality2Weka_WC_Unigram_Title(excelfile_2010, speciteller_datadir_2010, titledir_2010, wekafile, sheets=range(0,4), filters=filters)
          
    wekafile = "../data/weka/quality_CrossCourse_New_train.arff"
    WriteQuality2Weka_New(excelfile, speciteller_datadir, titledir, wekafile)
           
    wekafile = "../data/weka/quality_CrossCourse_New_test.arff"
    WriteQuality2Weka_New(excelfile_2010, speciteller_datadir_2010, titledir_2010, wekafile, sheets=range(0,4), filters=filters)
    #cross course end
   
   #cross course begin
    #remove title

#     wekafile = "../data/weka/quality_CrossCourse_DT_Title_train.arff"
#     WriteQuality2Weka_New_Title(excelfile, speciteller_datadir, titledir, wekafile)
#     
    #coursemirrorfile = "../../../../CourseMIRROR_server/data/CourseMirror/reflections.json"
    
 
#     wekafile = "../data/weka/quality_CrossCourse_DT_test.arff"
#     WriteQuality2Weka_DT_Title(excelfile_2010, speciteller_datadir_2010, titledir, wekafile, sheets=range(0,4))
#                  
#     wekafile = "../data/weka/quality_CrossCourse_WC_Unigram_train.arff"
#     WriteQuality2Weka_WC_Unigram_Title(excelfile, speciteller_datadir, titledir, wekafile)
#         
#     wekafile = "../data/weka/quality_CrossCourse_WC_Unigram_test.arff"
#     WriteQuality2Weka_WC_Unigram_Title(excelfile_2010, speciteller_datadir_2010, titledir, wekafile, sheets=range(0,4))
#       
#     wekafile = "../data/weka/quality_CrossCourse_New_train_title.arff"
#     WriteQuality2Weka_New_Title(excelfile, speciteller_datadir, titledir, wekafile)
#        
#     wekafile = "../data/weka/quality_CrossCourse_New_test_title.arff"
#     WriteQuality2Weka_New_Title(excelfile_2010, speciteller_datadir_2010, titledir, wekafile, sheets=range(0,4))
     
def getH3label():
    for label in ["../data/weka/quality_CrossCourse_New_test.label",
             "../data/weka/quality_CrossCourse_DT_test.label",
             "../data/weka/quality_CrossCourse_WC_Unigram_test.label"
             ]:
            
        formatTestlabel(label, label + ".new")

if __name__ == '__main__':
        
    excelfile = "../data/2011Spring.xls"
    speciteller_datadir = "../data/speciteller/"
    titledir = "E:/Dropbox/reflection project_LRDC/250 Sp11 CLIC All Lecs .2G/titles/"


    TestNewCourse()
    exit(0)
    
    #getQualityLengthDistribution(excelfile)
    #exit(0)
    
    #dis = "../data/q_dis.txt"
    #getQualityDistribution(excelfile, dis)
    
    prob = "../data/MP.prob"
    
    #getQualityText(excelfile, datadir)
    #getQualityText(excelfile_2010, speciteller_datadir_2010, sheets=range(0,4))
    
    #PostProcessProb(excelfile, speciteller_datadir)
    
    
    excelfile_2010 = "../data/2010Spring.xls"
    
    speciteller_datadir_2010 = "../data/speciteller_2010/"
    titledir_2010 = "E:/Dropbox/reflection project_LRDC/250 Sp11 CLIC All Lecs .2G/titles_2010/"
     
    #PostProcessProb(excelfile_2010, speciteller_datadir_2010, sheets=range(0,4))
   
#     wekafile = "../data/weka/quality_New-Title.arff"
#     WriteQuality2Weka_New_Title(excelfile, speciteller_datadir, titledir, wekafile)
 
    filters = [line.lower().strip() for line in fio.ReadFile('../data/filters.txt')]
    #getQualityLengthDistribution(excelfile_2010, sheets=range(0,4), filters=filters)
    
    #with title
 
#     wekafile = "../data/weka/quality_New.arff"
#     WriteQuality2Weka_New(excelfile, prob, titledir, wekafile)
#    
#     

#     wekafile = "../data/weka/quality_CrossLecture_New_Title"
#     WriteQuality2Weka_CrossLecture_New_Title(excelfile, prob, titledir, wekafile)

#    wekafile = "../data/weka/quality_CrossTopic_New_Title"
#    WriteQuality2Weka_CrossTopic_New_Title(excelfile, prob, titledir, wekafile)

    #fio.ExtractWekaScore("../../QualityPrediction/log.txt", "../data/weka/quality_2.txt")
    
    print "done"
