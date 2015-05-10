#!/usr/bin/python
from connection import register, ParseBase, ParseBatcher
import json

#from six.moves.urllib.parse import urlencode

import CourseMirrorSurvey


# from six.moves.urllib.request import Request, urlopen
# from six.moves.urllib.error import HTTPError
# from six.moves.urllib.parse import urlencode

URL_BASE = "https://api.parse.com";
URL_BATCH = "https://api.parse.com/1/batch"

URL_AUTH_FRAG = "/1/login";
URL_AUTH = URL_BASE + URL_AUTH_FRAG;

URL_USERS_FRAG =  "/1/users";
URL_USERS = URL_BASE + URL_USERS_FRAG;

URL_COURSES_FRAG = "/1/classes/Course";
URL_COURSES = URL_BASE + URL_COURSES_FRAG;

URL_LECTURES_FRAG = "/1/classes/Lecture";
URL_LECTURES = URL_BASE + URL_LECTURES_FRAG;

URL_REFLECTIONS_FRAG = "/1/classes/Reflection";                                               
URL_REFLECTIONS = URL_BASE + URL_REFLECTIONS_FRAG;

URL_SUMMARIZATION_FRAG = "/1/classes/Summarization";                                               
URL_SUMMARIZATION = URL_BASE + URL_SUMMARIZATION_FRAG;
        
PARSE_APP_ID = "YMGbDwY7f98JJQax7ErPyQHrjdGHXLKjzGcPCpUC";
PARSE_REST_API_KEY = "pEyDlfI7xPIg4qSrDwmvyldKoy1zlMzFLwZTiXAq";
PARSE_CLIENT_KEY = "5kwK971smxQ1FqDZy5djicIpZBTDimDET4DIwEt2";
HEADER_PARSE_REST_API_KEY = "X-Parse-REST-API-Key";
HEADER_PARSE_APP_ID = "X-Parse-Application-Id";
PARSE_MASTER_KEY = "cp1GtyipXhmQfE8kU3R9OkSPDF9qpkrOpRt6SE6L"

CONTENT_TYPE_JSON = "application/json";
USERNAME = "username";
PASSWORD = "password";
SESSION_TOKEN = "sessionToken";
    
register(
    PARSE_APP_ID,
    PARSE_REST_API_KEY,
    master_key=PARSE_MASTER_KEY
)

def getData(url, constraint = None):
    #the constraint is a dictionary
    parsebase = ParseBase()
    kw = json.dumps(constraint if constraint != None else {})
    data = parsebase.execute(url, "GET", None, False, where = kw)
    return data

def submitSingleBatchData(url_flag, datas):
    print url_flag
    print len(datas)
    
    parsebase = ParseBase()
    kw = []
    
    for data in datas:
        dict = {"method":"POST", "path":url_flag}
        dict["body"] = data
        kw.append(dict)
    response = parsebase.execute(URL_BATCH, "POST", None, False, requests=kw)
    return response

def submitData(url_flag, datas):
    #reflections are a list of dictionary
    responses = []
    
    #batch model
    N = len(datas)
    print N
    maxLimit = 10
    
    k = 0
    while k*maxLimit < N:
        try:
            response = submitSingleBatchData(url_flag, datas[maxLimit*k : maxLimit*(k+1)])
            responses.append(response)
        except Exception:
            pass
        
        k = k + 1
        
    return responses

def saveReflection(output):
    #the constraint is a dictionary
    reflections = getData(URL_REFLECTIONS)
    #reflections2 = getData(URL_REFLECTIONS + "/p1")
    
    f = open(output,'w')
    json.dump(reflections,f,indent=2)
    f.close()
    
def combineReflection(excelfile):
    reflections = CourseMirrorSurvey.getStudentResponse(excelfile)
    print reflections
    
    responses = submitData(URL_REFLECTIONS_FRAG, reflections)
    print responses
    
    
def submitSummary(dir, course, method, sheets):
    path = dir + course + "_" + method + "/"
    
    print path
    summaries = CourseMirrorSurvey.getSummary(path, course, sheets)
    #print len(summaries)
    print summaries
    #exit()
    
    for summary in summaries:
        summary['cid'] = course
        summary['method'] = method
        print summary

    responses = submitData(URL_SUMMARIZATION_FRAG, summaries)
    print responses
      
if __name__ == '__main__':
    #Step0: manually combine reflections
#     
    
    #combineReflection("CourseMIRROR PHYS0175 Reflections (Responses).xls")
    
    #saveReflection("../../Fall2014/summarization/Summarization/data/reflections.json")
    
    #Step9:
#     for course in ['PHYS0175']:
#         submitSummary("../../../mead/data/", course, "ClusterARank", sheets=range(38, 39))
    
    #combineReflection("CourseMIRROR IE256 Reflections (Responses).xls")
    for course in ['IE256']:
        submitSummary("../../../mead/data/", course, "ClusterARank", sheets=range(23, 25))
     
    print "done"