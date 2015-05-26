
import time, datetime
import json
import fio
import NLTKWrapper
import numpy

def getTime(j1, user, q1, q2, q3):
    for r in j1:
        if r['user'].lower() != user.lower(): continue
        if r['q1'].lower() != q1.lower(): continue
        if r['q2'].lower() != q2.lower(): continue
        
        if q3 == None: continue
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
        
        if 'q1' in r and 'q2' in r:
            q1 = r['q1']
            q2 = r['q2']
            #q3 = r['q3']
            
            t = getTime(j1, user, q1, q2, q3=None)
        else:
            t = None
        
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
    
    head = ['cid', 'lecture_number', 'date', 'user', 'submit', 'submitT', 'Lq1', 'Lq2']
    body = []
    
    times = {}
    d = 5*60
    
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
        
#         try:
#             submitT = t - due
#         except Exception as e:
#             print cid, lecture_number
#             print e
        if due == None:
            print cid, lecture_number
        submitT = t - due
        
        if submitT > -2000:
            key = int(submitT/d)
            
            if key not in times:
                 times[key] = 0
            times[key] = times[key] + 1
        
        row.append(submitT) #in seconds
        
        if 'q1' in r:
            row.append(len(NLTKWrapper.wordtokenizer(r['q1'], punct=True)))
        else:
            row.append(0)
        
        if 'q2' in r:
            row.append(len(NLTKWrapper.wordtokenizer(r['q2'], punct=True)))
        else:
            row.append(0)
        #row.append(len(NLTKWrapper.wordtokenizer(r['q3'], punct=True)))
        
        body.append(row)
    
    fio.WriteMatrix(output, body, head)
    
    N = 0
    for k, v in times.items():
        N = N + v
    
    for k in times:
        times[k] = float(times[k]) / N * 100
    
    fio.PrintDict(times)
    
    keys = times.keys()
    
    values = []
    for i in range(-4, 60):
        if i in times:
            values.append(times[i])
        else:
            values.append(0)
    fio.PrintList(values, '\n')
    
def extractDataLength(refs, lecs, course, output):
    f = open(refs,'r')
    reflections = json.load(f)
    f.close()
    
    f = open(lecs,'r')
    lectures = json.load(f)
    f.close()
    
    LengthList = []
    
    head = ['cid', 'lecture_number', 'date', 'user', 'submit', 'submitT', 'Lq1', 'Lq2', 'Lq3']
    body = []
    
    times = {}
    d = 5*60
    
    for r in reflections['results']:
        row = []
        
        cid = r['cid']
        if cid != course: continue
        
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
        
        if submitT > -2000:
            key = int(submitT/d)
            
            if key not in times:
                 times[key] = 0
            times[key] = times[key] + 1
        
        row.append(submitT) #in seconds
        
        LengthList.append(len(NLTKWrapper.wordtokenizer(r['q1'], punct=True)))
        LengthList.append(len(NLTKWrapper.wordtokenizer(r['q2'], punct=True)))
        LengthList.append(len(NLTKWrapper.wordtokenizer(r['q3'], punct=True)))
        
        row.append(len(NLTKWrapper.wordtokenizer(r['q1'], punct=True)))
        row.append(len(NLTKWrapper.wordtokenizer(r['q2'], punct=True)))
        row.append(len(NLTKWrapper.wordtokenizer(r['q3'], punct=True)))
        
        body.append(row)
    
    fio.SaveList(LengthList, output, "\n")
    print numpy.max(LengthList),'\t',numpy.min(LengthList),'\t',numpy.mean(LengthList),'\t',numpy.median(LengthList),'\t',numpy.std(LengthList)
    
            
def getUniqValue(matrix, col):
    values = [row[col] for row in matrix]    
    return set(values)

def getUniqValueWithFilter(head, body, filtername, filtervalue, col):
    index = head.index(filtername)
    
    values = []
    for row in body:
        if row[index] != filtervalue: continue
        values.append(row[col])
    
    values = set(values)
    return sorted(values)

def findReflection(body, ci, ni, ui, c, n , u):
    count = 0
    R = None
    for row in body:
        if row[ci] != c: continue
        if row[ni] != n: continue
        if row[ui] != u: continue
        count = count + 1
        R = row
        #return row
    if count > 1:
        print c, n, u
    return R
           
def getSubmisstionRatio(datafile, lecturefile, output):
    f = open(lecturefile,'r')
    lectureinfo = json.load(f)
    f.close()
    
    head, body = fio.ReadMatrix(datafile, True)
    
    course_index = head.index('cid')
    user_index = head.index('user')
    lecture_index = head.index('lecture_number')
    
    for cid in ['PHYS0175', 'IE256']:
        users = getUniqValueWithFilter(head, body, 'cid', cid, user_index)
        lectures = getUniqValueWithFilter(head, body, 'cid', cid, lecture_index)
        lectures = sorted([int(lec) for lec in lectures])
        lectures = [str(lec) for lec in lectures]
        
        ratioHead = ['cid', 'lecture_number', 'date', 'sumbitedN', 'ratio', 'Ave_submitT', 'Ave_Lq1', 'Ave_Lq2', 'Std_submitT', 'Std_Lq1', 'Std_Lq2',]
        ratioBody = []
        
        newhead = ['cid', 'lecture_number', 'date', 'user', 'submit', 'submitT', 'Lq1', 'Lq2',]
        newbody = []
        for lec in lectures:
            date = getDate(lectureinfo, cid, int(lec))
            ratioRow = [cid, lec, date]
            
            count = 0
            
            Ave = []
            for user in users:
                newrow = findReflection(body, course_index, lecture_index, user_index, cid, lec, user)
                if newrow == None:
                    newrow = [cid, lec, date]
                    newrow = newrow + [user, 'N', 0, 0, 0]
                else:
                    count = count + 1
                    Ave.append(newrow[-3:])
                    
                newbody.append(newrow)
                
            ratioRow.append(count)
            ratioRow.append(float(count) / len(users))

            for i in range(3):
                values = [float(xx[i]) for xx in Ave]
                ratioRow.append(numpy.average(values))
            
            for i in range(3):
                values = [float(xx[i]) for xx in Ave]
                ratioRow.append(numpy.std(values))
                
            ratioBody.append(ratioRow)
            
        fio.WriteMatrix(output+"_"+cid + ".txt", newbody, newhead)
        fio.WriteMatrix(output+"_"+cid + "_ratio.txt", ratioBody, ratioHead)

def getUserSubmisstionInfo(datafile, lecturefile, output):
    f = open(lecturefile,'r')
    lectureinfo = json.load(f)
    f.close()
    
    head, body = fio.ReadMatrix(datafile, True)
    
    course_index = head.index('cid')
    user_index = head.index('user')
    lecture_index = head.index('lecture_number')
    
    for cid in ['PHYS0175', 'IE256']:
        users = getUniqValueWithFilter(head, body, 'cid', cid, user_index)
        lectures = getUniqValueWithFilter(head, body, 'cid', cid, lecture_index)
        lectures = sorted([int(lec) for lec in lectures])
        lectures = [str(lec) for lec in lectures]
        
        newhead = ['user', 'cid', 'lecture_number', 'date', 'submit', 'submitT', 'Lq1', 'Lq2']
        newbody = []
        
        ratioHead = ['user', 'SumbmitN', 'ratio', 'Ave_submitT', 'Ave_Lq1', 'Ave_Lq2', 'Std_submitT', 'Std_Lq1', 'Std_Lq2']
        ratioBody = []
        for user in users:
            ratioRow = [user]
            
            count = 0
            Ave = []
            for lec in lectures:
                newrow = [user, cid]
                newrow.append(lec)
                date = getDate(lectureinfo, cid, int(lec))
                newrow.append(date)
                
                trow = findReflection(body, course_index, lecture_index, user_index, cid, lec, user)
                if trow == None:
                    newrow = newrow + ['N', 0, 0, 0]
                else:
                    newrow = newrow + trow[-4:]
                    Ave.append(newrow[-3:])
                    count = count + 1
                
                newbody.append(newrow)
             
            ratioRow.append(count)
            ratioRow.append(float(count) / len(lectures))

            for i in range(3):
                values = [float(xx[i]) for xx in Ave]
                ratioRow.append(numpy.average(values))
            
            for i in range(3):
                values = [float(xx[i]) for xx in Ave]
                ratioRow.append(numpy.std(values))
                
            ratioBody.append(ratioRow)
               
        fio.WriteMatrix(output+"_"+cid + ".txt", newbody, newhead)
        fio.WriteMatrix(output+"_"+cid + "_ratio.txt", ratioBody, ratioHead)        
        
if __name__ == '__main__':
    
    reflect_raw = "../../data/CourseMirror/Reflection.json"
    reflect_raw_time = "../../data/CourseMirror/Reflection_time.json"
    lecture_raw = "../../data/CourseMirror/Lecture.json"
    lecture_raw_time = "../../data/CourseMirror/Lecture_time.json"
    
    CombineTimeStamp('CourseMIRROR_reflections.json', reflect_raw, reflect_raw_time)
    AddDueTimeforLecture(lecture_raw, lecture_raw_time)
    
    datafile = "user_lecture.txt"
    extractData(reflect_raw_time, lecture_raw_time, datafile)
    
    #extractDataLength("reflection_time.json", 'lecture_time.json', "CS2610", "CS2610_Length.txt")
    
    outputprefix = "all_user_lecture"
    getSubmisstionRatio(datafile, lecture_raw_time, outputprefix)
    
    outputprefix = "all_users"
    getUserSubmisstionInfo(datafile, lecture_raw_time, outputprefix)
    print "done"
    
    
    