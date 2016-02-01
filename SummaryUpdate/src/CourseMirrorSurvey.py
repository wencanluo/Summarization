from OrigReader import prData
import sys
import re
import fio
import json
import codecs

course = "PHYS0175"

range2 = range(2,24)
range3 = range(3,42)
range4 = range(1,26)

maxWeekDict = {"CS2610": 21-4+1, 
               "CS2001": len(range2),
               "PHYS0175":len(range3),
               "IE256":len(range4),
               }

WeekLecture = {"CS2610":range(4, 40),
               "CS2001":range2,
               "PHYS0175": range3,
               "IE256": range4,
               }
header = ['cid', 'lecture_number', 'user', 'q1', 'q2']
TpyeMap = {"POI":'q1_summaries', "MP":'q2_summaries', "LP":'q3_summaries'}

RatingKey = {"slightly": 1, 
"somewhat": 2,
"moderately": 3, 
"mostly":4,
"completely":5
}

RateSplitTag = "||Rating: "

def getRatingkey(rate):
    key = rate.strip().lower()
    if key in RatingKey:
        return RatingKey[key]
    return -1

def NormalizeResponse(response):
    k = response.find(RateSplitTag)
    if k == -1:
        return response
    return response[:k]

def getStudentResponseRaw(excelfile):
    '''
    return a list of dictionary of the students' summary
    '''
    orig = prData(excelfile, 0)
    tokenIndex = 'user'
    couseIndex = 'cid'
    lectureIndex = 'lecture_number'
    
    reflections = []
    
    for k, inst in enumerate(orig._data):
        try:
            token = str(inst[tokenIndex]).lower().strip()
            
            if len(token) > 0:
                
                dict = {}
                for key in orig._fea:
                    if key == "lecture_number":
                        dict[key] = int(inst[key])
                    elif key == "user":
                        dict[key] = str(inst[key]).strip().lower()
                    else:
                        dict[key] = inst[key]
                
                if 'q1_rate' in inst:
                    dict["q1"] = dict["q1"] + RateSplitTag + str(getRatingkey(inst['q1_rate']))
                if 'q2_rate' in inst:
                    dict["q2"] = dict["q2"] + RateSplitTag + str(getRatingkey(inst['q2_rate']))
                
                reflections.append(dict)
            else:
                break
        except Exception as e:
            print e
            return []
    return reflections

def GoogleStudentResponsetoJson(excelfiles, output):
    reflections = []
    
    for excelfile in excelfiles:
        reflection = getStudentResponseRaw(excelfile)
        reflections += reflection
    
    with codecs.open(output, 'w', 'utf-8') as fout:
        json.dump(reflections, fout, indent=2)
            
def getStudentResponse(excelfile):
    '''
    return a list of dictionary of the students' summary
    '''
    orig = prData(excelfile, 0)
    tokenIndex = 'user'
    couseIndex = 'cid'
    lectureIndex = 'lecture_number'
    
    reflections = []
    
    for k, inst in enumerate(orig._data):
        try:
            token = str(inst[tokenIndex]).lower().strip()
            
            if len(token) > 0:
                
                dict = {}
                for key in header:
                    if key == "lecture_number":
                        dict[key] = int(inst[key])
                    elif key == "user":
                        dict[key] = str(inst[key]).strip().lower()
                    else:
                        dict[key] = inst[key].strip()
                
                if 'q1_rate' in inst:
                    dict["q1"] = dict["q1"] + RateSplitTag + str(getRatingkey(inst['q1_rate']))
                if 'q2_rate' in inst:
                    dict["q2"] = dict["q2"] + RateSplitTag + str(getRatingkey(inst['q2_rate']))
                
                reflections.append(dict)
            else:
                break
        except Exception as e:
            print e
            return []
    return reflections

def getSummary(datadir, course, sheets = None):
    #return a list of summaries, week by week. The summary for each week is also a list
    
    if sheets == None:
        maxWeek = maxWeekDict[course]
        print maxWeek
        
        sheets = range(0, maxWeek)
        
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    
    summaries = []
    
    for sheet in sheets:
        dict = {}
        
        week = sheet + 1
        
        path = datadir + str(week)+ '/'
        if not fio.IsExistPath(path): continue
        
        dict['lecture_number'] = WeekLecture[course][sheet]
        
        for type in ['POI', 'MP', 'LP']:
            filename = path + type + '.summary'
            if not fio.IsExist(filename): continue
            print filename
            
            lines = fio.ReadFile(filename)
            if len(lines) == 0: continue
            
            summary = []
            weight = []
            
            for line in lines:
                summary.append(line.decode('latin-1').strip())
            
            summarydict = {}
            summarydict['summaryText'] = summary
            
            sourcefile = path + type + '.summary.source'
            if not fio.IsExist(sourcefile):
                for s in summary:
                    weight.append(1.0)
            else:
                sources = [line.strip().split(",") for line in fio.ReadFile(sourcefile)]
                
                assert(len(sources) == len(summary))
                summarydict['Sources'] = sources
                
                for source in sources:
                    weight.append(len(source))
                
            summarydict['weight'] = weight
            dict[TpyeMap[type]] = json.dumps(summarydict)
            
        summaries.append(dict)
    
    return summaries

if __name__ == '__main__':
    pass
    