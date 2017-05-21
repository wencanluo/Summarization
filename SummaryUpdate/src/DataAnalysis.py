import time, datetime
import json
import fio
import NLTKWrapper
import numpy
import CourseMirrorSurvey

def getTime(j1, user, lecture, q1, q2, q3):
    for r in j1:
        if r['user'].lower() != user.lower(): continue
        if r['q1'].lower() != q1.lower(): continue
        if r['q2'].lower() != q2.lower(): continue
        if lecture != None:
            if r['lecture_number'] != lecture: continue
        
        if q3 != None:
            if r['q3'].lower() != q3: continue
        
        return r['Timestamp']
    return None

def exceltime2python(t):
    return (t - 25569) * 86400.0
    
def get_time_distribution(reflections_json, cid, lecture_time_json, output):
    f = open(reflections_json,'r')
    data = json.load(f)
    f.close()
    
    f = open(lecture_time_json,'r')
    lecture_time = json.load(f)
    f.close()
    
    times = {}
    d = 5*60
    
    for ref in data:
        if ref['cid'] == cid:
            t = ref['Timestamp']
            t = time.strptime(t, "%m/%d/%Y %H:%M:%S")
            t = time.mktime(t)
            
            tt = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(t))
            #print tt
            
            lecture = ref['lecture_number']
            due_t = getDueTime(lecture_time, cid, lecture)
            tt = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(due_t))
            #print tt
            
            if due_t == None:
                print lecture
                
            dt = t - due_t
            #print dt
            
    
            if dt > -2000:
                key = int(dt/d)
            
                if key not in times:
                     times[key] = 0
                times[key] = times[key] + 1
    
    keys = times.keys()
    
    values = []
    for i in range(numpy.min(keys), numpy.max(keys) + 1):
        if i in times:
            #values.append(times[i])
            if i%6 == 0:
                print i, '\t', i/12., '\t', times[i]
            else:
                print i, '\t', '', '\t', times[i]
        else:
            #values.append(0)
            if i%6 == 0:
                print i, '\t', i/12., '\t', 0
            else:
                print i, '\t', '', '\t', 0
            
    #fio.PrintList(values, '\n')
                
def CombineTimeStamp(json1, json2, output):
    
    f = open(json1,'r')
    j1 = json.load(f)
    f.close()
    
    f = open(json2,'r')
    j2 = json.load(f)
    f.close()
        
    for r in j2['results']:
        user = r['user']
        
        if r['cid'] == 'CS2001' or r['cid'] == 'CS2610':
            t = None
        else:
            if 'q1' in r and 'q2' in r:
                q1 = r['q1'].split('||')[0]
                q2 = r['q2'].split('||')[0]
                #q3 = r['q3']
                
                if user == 'm1994':
                    debug = 1
                lecture = r['lecture_number']
                
                t = getTime(j1, user, lecture, q1, q2, q3=None)
                
                if t != None:
                    #t0 = (datetime.datetime(1970,1,1) - datetime.datetime(1899,12,30)).total_seconds()
                    
                    t = exceltime2python(t)
                    #t = t+t0
                
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
        elif r['cid'] == 'CS2610':
            t = "15:45:00"
        elif r['cid'] == 'PHYS0175':
            lecture_date = r['date']
            
            date_object = time.strptime(lecture_date, '%m/%d/%Y')
            
            if date_object.tm_wday == 2:
                t = '09:50:00'
            else:
                t = '08:50:00'
        elif r['cid'] == 'IE256':
            lecture_date = r['date']
            
            date_object = time.strptime(lecture_date, '%m/%d/%Y')
            
            if date_object.tm_wday == 1:
                t = '02:50:00'
            else:
                t = '03:50:00'
        
            
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
        
        t = lec['date'] + ' ' + lec['Due']
        
        t = time.strptime(t, "%m/%d/%Y %H:%M:%S")
        t = time.mktime(t)
        #est_t = eastern.localize(t)
        
        #t = datetime.datetime.strptime(t, "%m/%d/%Y %H:%M:%S")
        #t = time.mktime(est_t.timetuple())
        #t = t.replace(tzinfo=pytz.timezone('US/Eastern'))
        
        #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(t))
        
        #t = time.mktime(t.timetuple())
        return t
        
    return None
        
def extractData(refs, lecs, output):
    f = open(refs,'r')
    reflections = json.load(f)
    f.close()
    
    f = open(lecs,'r')
    lectures = json.load(f)
    f.close()
    
    head = ['cid', 'lecture_number', 'date', 'user', 'submit', 'Lq1', 'Lq2']
    body = []
    

    for r in reflections['results']:
        row = []
        
        cid = r['cid']
        row.append(cid)
        
        lecture_number = r['lecture_number']
        row.append(lecture_number)
        
        date = getDate(lectures, cid, lecture_number)
        row.append(date)
        
        row.append(r['user'].lower())
        
        row.append('Y') #sumbit
              
        if 'q1' in r:
            row.append(len(NLTKWrapper.wordtokenizer(r['q1'], punct=True)))
        else:
            row.append(0)
        
        if 'q2' in r:
            row.append(len(NLTKWrapper.wordtokenizer(r['q2'], punct=True)))
        else:
            row.append(0)
        
        body.append(row)
    
    fio.WriteMatrix(output, body, head)
    
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
    
    for cid in ['ENGR_132']:
        users = getUniqValueWithFilter(head, body, 'cid', cid, user_index)
        lectures = getUniqValueWithFilter(head, body, 'cid', cid, lecture_index)
        lectures = sorted([int(lec) for lec in lectures])
        lectures = [str(lec) for lec in lectures]
        
        newhead = ['user', 'cid', 'lecture_number', 'date', 'submit', 'Lq1', 'Lq2']
        newbody = []
        
        ratioHead = ['user', 'SumbmitN', 'ratio', 'Ave_Lq1', 'Ave_Lq2', 'Std_Lq1', 'Std_Lq2']
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
                    newrow = newrow + ['N', 0, 0]
                else:
                    newrow = newrow + trow[-3:]
                    Ave.append(newrow[-2:])
                    count = count + 1
                
                newbody.append(newrow)
             
            ratioRow.append(count)
            ratioRow.append(float(count) / len(lectures))

            for i in range(2):
                values = [float(xx[i]) for xx in Ave]
                ratioRow.append(numpy.average(values))
            
            for i in range(2):
                values = [float(xx[i]) for xx in Ave]
                ratioRow.append(numpy.std(values))
                
            ratioBody.append(ratioRow)
               
        fio.WriteMatrix(output+"_"+cid + ".txt", newbody, newhead)
        fio.WriteMatrix(output+"_"+cid + "_ratio.txt", ratioBody, ratioHead)        
        
if __name__ == '__main__':
    
    reflect_raw = "../../data/CourseMirror/reflections.json"
    lecture_raw = "../../data/CourseMirror/lectures.json"
    
    datafile = "user_lecture.txt"
    extractData(reflect_raw, lecture_raw, datafile)
    
    outputprefix = "all_users"
    getUserSubmisstionInfo(datafile, lecture_raw, outputprefix)
    print "done"
    
    
    