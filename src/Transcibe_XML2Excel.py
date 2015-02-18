import xlrd, xlwt
import xml.etree.ElementTree as ET
import os
import re
import time

RoleDict = {"002": "Engineer",
            "003": "Messenger",
            "004": "Pilot",
            "005": "Explorer",
            }

def getRole(linenumber):
    if linenumber in RoleDict:
        return RoleDict[linenumber]
    return "NAN"
    
def GetTranscription(node):
    trasncription = []
    for t in node:
        if t.text == None: continue
        trasncription.append(t.text)
    return " ".join(trasncription)

def getNameSpace(tag):
    key = tag.find("}")
    if key != -1:
        return tag[:key+1]
    return ""

def getChildbyTag(root, name):
    childs = []
    for child in root:
        if name in child.tag:
            childs.append(child)
    return childs

def Write2Excel(head, data, xls): #the last entry in data in features
    
    GameIndex = head.index("Game1or2")
    GameNumber = data[0][GameIndex]
    
    #get feature names
    keys = set([])
    for row in data:
        features = row[-1]
        keys = keys.union(set(features.keys()))
    
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Game'+str(GameNumber))
    
    i = 0
    for name in head:
        sheet.write(0, i, name)
        i = i+1
    for key in keys:
        sheet.write(0, i, key)
        i = i+1
    
    for index, row in enumerate(data):
        i = index+1
        for j, col in enumerate(row):
            if j == len(row)-1:
                dict = col
                k = j
                for key in keys:
                    if key in dict:
                        sheet.write(i, k, dict[key])
                    else:
                        sheet.write(i, k, "")
                    k = k + 1
            else:
                sheet.write(i, j, col)

    workbook.save(xls)

def getDatefromFileName(path):#last modified time
    #time.ctime(os.path.getctime(file))
    return time.ctime(os.path.getmtime(path))
    
    
def getTeamInfo(path):
    dict = {}
    dict['path'] = path
    
    head, tail = os.path.split(path)
    regex = re.compile("Team (\d+) Game (\d+)-(\d+).wav")
    r = regex.search(tail)
    
    if len(r.groups()) == 3:
        dict['team'] = r.group(1)
        dict['game'] = r.group(2)
        dict['track'] = r.group(3)
        dict['role'] = getRole(r.group(3))
    return dict

def NormalizedTranscription(utterance):
    utterance = utterance.lower()
    utterance = re.sub(r"\(.*\)", "", utterance)
    utterance = utterance.replace(".", "")
    utterance = utterance.replace(",", "")
    utterance = utterance.replace("?", "")
    return utterance.strip()
    #remove 
    #remove punctuation

def getUtterance(path, xml):
    
    Utterances = {}
    tree = ET.parse(path + xml)
    root = tree.getroot()
 
    tracks = getChildbyTag(root, "tracks")[0]
    segments = getChildbyTag(root, "segments")[0]
    
    #get segments
    for segment in segments:
        source_id = segment.attrib['source']
         
        transcriptionNodes = getChildbyTag(segment, 'transcription')
        if len(transcriptionNodes) < 1:
            transcription = ""
        else:
            transcription = GetTranscription(transcriptionNodes[0])
        #print transcription
        if len(transcription) == 0:continue
        
        transcription = NormalizedTranscription(transcription)
        
        if source_id not in Utterances:
            Utterances[source_id] = []
        Utterances[source_id].append(transcription)
    
    return Utterances
    
def XML2Excel(path, xml, output):
    head = ['TeamID', 'Video_Filename', 'Audio_Filename', 'Date', 'Game1or2', 'Game_Order', 'Line_Number', 'Speaker_Role', 'Timestamp_Start', 'Timestamp_End', 'Utterance']
    tree = ET.parse(path + xml)
    root = tree.getroot()
    
    id = root.attrib['id']
    print id
    
    tracks = getChildbyTag(root, "tracks")[0]
    segments = getChildbyTag(root, "segments")[0]
    
    #get tracks
    role = {}
    
    sources = {}
    for track in tracks:
        sourceID = track[0][0].attrib['id']
        filename = track[0][0].attrib['href']
        sources[sourceID] = getTeamInfo(filename)
 
    body = []
    #get segments
    for segment in segments:
        row = []
        row.append(id)
        
        row.append("")#Video_Filename
        
        start_t = segment.attrib['start']
        end_t = segment.attrib['end']
        source_id = segment.attrib['source']
        teaminfo = sources[source_id]
        
        Audio_Filename = teaminfo['path']
        
        row.append(Audio_Filename) #Audio_Filename
        #Date = getDatefromFileName(Audio_Filename) #Date
        row.append("NAN")
        
        Game1or2 =  teaminfo['game']
        row.append(Game1or2)
        
        row.append("NAN") #Game_Order
        Speaker_Role = teaminfo['role']
        row.append(teaminfo['track'])
        row.append(Speaker_Role)
        
        row.append(start_t)
        row.append(end_t)

        transcriptionNodes = getChildbyTag(segment, 'transcription')
        if len(transcriptionNodes) < 1:
            transcription = ""
        else:
            transcription = GetTranscription(transcriptionNodes[0])
        
        row.append(transcription)
        
        features = {}
        
        featureNodes = getChildbyTag(segment, 'features')
        if len(featureNodes) > 0:
            featureNode = featureNodes[0]
                
            for feature in featureNode:
                features[feature.attrib['name']] = feature.text
            
        #print source_id, start_t, end_t, transcription
        row.append(features)
        body.append(row)
    
    Write2Excel(head, body, output)

if __name__ == '__main__':
    path = "E:/project/Audio/"
    xml = "ref.xml"
    
    #XML2Excel(path, xml, path + "Team1251.xls")
    ut = NormalizedTranscription("(--) Ok. Um shore up two tiles for one action. We do?")
    print ut
    
    print "done"