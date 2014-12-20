
import time, datetime
import json
import fio
import NLTKWrapper

def getTime(j1, user, q1, q2, q3):
    for r in j1:
        if r['user'].lower() != user.lower(): continue
        if r['q1'].lower() != q1.lower(): continue
        if r['q2'].lower() != q2.lower(): continue
        if r['q3'].lower() != q3: continue
        
        return r['Timestamp']
    return None

def CombineTimeStamp(json1, json2, output):
    
    f = open(json1,'r')
    j1 = json.load(f)
    f.close()
    
    f = open(json2,'r')
    j2 = json.load(f)
    f.close()
        
    for r in j2['results']:
        user = r['user']
        q1 = r['q1']
        q2 = r['q2']
        q3 = r['q3']
        
        t = getTime(j1, user, q1, q2, q3)
        
        if t == None:
            t = r['createdAt']
            t = time.strptime(t, "%Y-%m-%dT%H:%M:%S.%fZ")
            t = time.mktime(t)
            t = t - 10*60*60
            
        r['TimeStamp'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(t))
    
    f = open(output,'w')
    json.dump(j2,f,indent=2)
    f.close()
    
def AddDueTimeforLecture(jfile, output):
    f = open(jfile,'r')
    lectures = json.load(f)
    f.close()
    
    for r in lectures['results']:
        if r['cid'] == 'CS2001':
            t = "14:15:00"
        else:
            t = "15:45:00"
            
        r['Due'] = r['date'] + ' ' + t
    
    f = open(output,'w')
    json.dump(lectures,f,indent=2)
    f.close()

def getDate(lectures, cid, lecture_number):
    
    for lec in lectures['results']:
        if lec['cid'] != cid: continue
        if lec['number'] != lecture_number: continue
        return lec['date']
        
    return None

def getDueTime(lectures, cid, lecture_number):
    for lec in lectures['results']:
        if lec['cid'] != cid: continue
        if lec['number'] != lecture_number: continue
        
        t = lec['Due']
        t = time.strptime(t, "%m/%d/%Y %H:%M:%S")
        t = time.mktime(t)
        return t
        
    return None
        
def extractData(refs, lecs, output):
    f = open(refs,'r')
    reflections = json.load(f)
    f.close()
    
    f = open(lecs,'r')
    lectures = json.load(f)
    f.close()
    
    head = ['cid', 'lecture_number', 'date', 'user', 'submit', 'submitT', 'Lq1', 'Lq2', 'Lq3']
    body = []
    
    for r in reflections['results']:
        row = []
        
        cid = r['cid']
        row.append(cid)
        
        lecture_number = r['lecture_number']
        row.append(lecture_number)
        
        date = getDate(lectures, cid, lecture_number)
        row.append(date)
        
        row.append(r['user'])
        
        row.append('Y') #sumbit
        
        due = getDueTime(lectures, cid, lecture_number)
        
        t = r['TimeStamp']
        t = time.strptime(t, "%Y-%m-%d %H:%M:%S")
        t = time.mktime(t)
        submitT = t - due
        row.append(submitT) #in seconds
        
        row.append(len(NLTKWrapper.wordtokenizer(r['q1'], punct=True)))
        row.append(len(NLTKWrapper.wordtokenizer(r['q2'], punct=True)))
        row.append(len(NLTKWrapper.wordtokenizer(r['q3'], punct=True)))
        
        body.append(row)
    
    fio.writeMatrix(output, body, head)

def getUniqValue(matrix, col):
    values = [row[col] for row in matrix]    
    return set(values)

def getUniqValueWithFilter(head, body, filtername, filtervalue, col):
    index = head.index(filtername)
    
    values = []
    for row in body:
        if row[index] != filtervalue: continue
        values.append(row[col])
    
    return set(values)
           
def getSubmisstionRatio(datafile, output):
    head, body = fio.readMatrix(datafile, True)
    
    user_index = head.index('user')
    lecture_index = head.index('lecture_number')
    
    for course in ['CS2610', 'CS2001']:
        users = getUniqValueWithFilter(head, body, 'cid', course, user_index)
        lectures = getUniqValueWithFilter(head, body, 'cid', course, lecture_index)
        
        head = ['cid', 'lecture_number', 'date', 'user', 'submit', 'submitT', 'Lq1', 'Lq2', 'Lq3']
        body = []
        for lec in lectures:
            for user in users:
                row = []
                row.append(course)
                row.append(lec)
                row.append()
        
        
if __name__ == '__main__':
    
    #CombineTimeStamp('CourseMIRROR_reflections.json', 'Reflection.json', "reflection_time.json")
    #AddDueTimeforLecture('Lecture.json', 'lecture_time.json')
    
    datafile = "user_lecture.txt"
    #extractData("reflection_time.json", 'lecture_time.json', datafile)
    
    outputprefix = "all_user_lecture"
    getSubmisstionRatio(datafile, outputprefix)    
    print "done"
    
    
    