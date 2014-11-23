import Survey, fio
from OrigReader import prData

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

def WriteQuality2Weka(excelfile, output):
    MPs = getQuality(excelfile)
    
    head = []
    #head = head + ['Text']
    head = head + ['Length']
    head = head + ['@class@']
    
    types = []
    #types = types + ['String']
    types = types + ['Continuous']
    types = types + ['Category']
    
    data = []
    for MP, score in MPs:
        row = []
        
        N = len(MP.split())
        
        #row.append(MP)
        row.append(N)
        row.append(score)
        
        data.append(row)
   
    fio.ArffWriter(output, head, types, "Quality", data)    
    
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    
    wekafile = "../data/quality.arff"
    
    WriteQuality2Weka(excelfile, wekafile)
    

