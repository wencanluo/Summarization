from OrigReader import prData
import sys
import re
import fio
import json

course = "CS2001"
#course = "CS2610"
maxWeekDict = {"CS2610": 21, 
               "CS2001": 18}

WeekLecture = {"CS2610":range(4, 40),
               "CS2001":range(5, 40)}

header = ['cid', 'lecture_number', 'user', 'q1', 'q2', 'q3']
TpyeMap = {"POI":'q1_summaries', "MP":'q2_summaries', "LP":'q3_summaries'}
            
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
            token = inst[tokenIndex].lower().strip()
            
            if len(token) > 0:
                
                dict = {}
                for key in header:
                    if key == "lecture_number":
                        dict[key] = int(inst[key])
                    elif key == "user":
                        dict[key] = inst[key].strip().lower()
                    else:
                        dict[key] = inst[key].strip()
                
                reflections.append(dict)
            else:
                break
        except Exception:
            return []
    return reflections

def getSummary(datadir, course):
    #return a list of summaries, week by week. The summary for each week is also a list
    
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
        if not fio.isExistPath(path): continue
        
        dict['lecture_number'] = WeekLecture[course][sheet]
        
        for type in ['POI', 'MP', 'LP']:
            filename = path + type + '.summary'
            if not fio.isExist(filename): continue
            print filename
            
            lines = fio.readfile(filename)
            if len(lines) == 0: continue
            
            summary = []
            weight = []
            
            for line in lines:
                summary.append(line.decode('latin-1').strip())
            
            summarydict = {}
            summarydict['summaryText'] = summary
            
            sourcefile = path + type + '.summary.source'
            if not fio.isExist(sourcefile):
                for s in summary:
                    weight.append(1.0)
            else:
                sources = [line.strip().split(",") for line in fio.readfile(sourcefile)]
                
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
    