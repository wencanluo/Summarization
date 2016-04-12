import fio
import Survey

def FormatOutputMead(datadir, rate = "word", R = 30):
    sheets = range(0,25)
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        for type in ['POI', 'MP', 'LP']:
            #read the output
            path = datadir + str(week)+ '/'
            filename = path + type + '.summary.org'
            if not fio.IsExistPath(path): continue
            
            lines = fio.ReadFile(filename)
            summaries = []
            for line in lines:
                summaries.append(Survey.NormalizeMeadSummary(line))
            
            #Format it
            import phraseClusteringKmedoid
            summaries = phraseClusteringKmedoid.MalformedNPFlilter(summaries)
                
            #Write it
            newSummary = []
            index = 1
            added = []
            total_word = 0
            for summary in summaries:
                if summary in added: continue
                
                word_count = len(summary.split())
                total_word = total_word + word_count
                
                if rate == "word":
                    if total_word <= R:
                        newSummary.append('[' + str(index) + ']  ' + summary)
                        index = index + 1
                    else:
                        total_word = total_word - word_count
                else:
                    if len(newSummary) + 1 <= R:
                        newSummary.append('[' + str(index) + ']  ' + summary)
                        index = index + 1
            
            #print newSummary
            filename = path + type + '.summary'
            fio.SaveList(newSummary, filename)

def getTotalWords(file):
    lines = fio.ReadFile(file)
    summaries = []
    for line in lines:
        summaries.append(Survey.NormalizeMeadSummary(line))
    
    #Format it
    import phraseClusteringKmedoid
    summaries = phraseClusteringKmedoid.MalformedNPFlilter(summaries)
    
    total_word = 0
    for summary in summaries:
        word_count = len(summary.split())
        total_word = total_word + word_count
    
    return total_word
                    
def FormatOutputMeadMMR(datadir, rate = "word", R = 30, ratio = 1.0, w=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]):
    #get Summary for a paticular parameter
    sheets = range(0,26)
    w.reverse()
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        for type in ['POI', 'MP']:
            
            wordcount = []
            
            for r in w:
                #read the output
                path = datadir + str(week)+ '/'
                #filename = path + type + '.' + str(ratio)+ '.summary.'+str(r)+'.org'
                filename = path + type + '.summary.'+str(r)+'.org'
                
                if not fio.IsExist(filename): break
                
                N = getTotalWords(filename)
                print N, R
                
                if N <= R:
                    lines = fio.ReadFile(filename)
                    summaries = []
                    for line in lines:
                        summaries.append(Survey.NormalizeMeadSummary(line))
                    
                    #Format it
                    #import phraseClusteringKmedoid
                    #summaries = phraseClusteringKmedoid.MalformedNPFlilter(summaries)
    
                    #Write it
                    newSummary = []
                    index = 1
                    added = []
                    total_word = 0
                    for summary in summaries:
                        if summary in added: continue
                        
                        word_count = len(summary.split())
                        total_word = total_word + word_count
                        
                        if rate == "word":
                            if total_word <= R:
                                newSummary.append('[' + str(index) + ']  ' + summary)
                                index = index + 1
                        else:
                            if len(newSummary) + 1 <= R:
                                newSummary.append('[' + str(index) + ']  ' + summary)
                                index = index + 1
                    
                    #print newSummary
                    filename = path + type + '.summary'
                    fio.SaveList(newSummary, filename)
                    break

def FormatOutputMeadMMR2(datadir, rate = "word", R = 30):
    sheets = range(0,12)
    for i, sheet in enumerate(sheets):
        week = i + 1
        
        for type in ['POI', 'MP', 'LP']:
            
            for r in ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0']:
                #read the output
                path = datadir + str(week)+ '/'
                filename = path + type + '.' + str(r) + '.summary.org'
                
                lines = fio.ReadFile(filename)
                summaries = []
                for line in lines:
                    summaries.append(Survey.NormalizeMeadSummary(line))
                
                #Format it
                import phraseClusteringKmedoid
                summaries = phraseClusteringKmedoid.MalformedNPFlilter(summaries)
                
                #Write it
                newSummary = []
                index = 1
                added = []
                total_word = 0
                for summary in summaries:
                    if summary in added: continue
                    
                    word_count = len(summary.split())
                    total_word = total_word + word_count
                    
                    if rate == "word":
                        if total_word <= R:
                            newSummary.append('[' + str(index) + ']  ' + summary)
                            index = index + 1
                    else:
                        if len(newSummary) + 1 <= R:
                            newSummary.append('[' + str(index) + ']  ' + summary)
                            index = index + 1
                
                #print newSummary
                filename = path + type + '.' + str(r) + '.summary'
                fio.SaveList(newSummary, filename)
                            
if __name__ == '__main__':
    
    rate = "word"
    R = 16
    
    excelfile = "../data/2011Spring.xls"
    sennadir = "../data/senna/"
    phrasedir = "../data/phrases/"
    outputdir = "../data/np/"
    #for np in ['chunk', 'syntax', ]:#'candidate', 'candidatestemming']:
    for np in ['syntax', ]:#'candidate', 'candidatestemming']:
        #for model in ['C30_PhraseMead_syntax', 'C30_PhraseMeadLexRank_syntax', 'C30_LexRank_syntax']:
        for model in ['IE256_C16/PhraseMeadMMR',]:
            datadir = "../../mead/data/"+model+"/"
            FormatOutputMeadMMR(datadir, rate, R, ratio=0.8, w=[1,2,3,4,5,6,7,8])
        
        for model in ['IE256_C16/PhraseLexRankMMR']:
            datadir = "../../mead/data/"+model+"/"
            FormatOutputMeadMMR(datadir, rate, R, ratio=0.7, w=[1,2,3,4,5,6,7,8])
            #FormatOutputMeadMMR2(datadir, rate, R)
            #FormatOutputMead(datadir, rate, R)
            #Survey.WriteTASummary(excelfile, datadir)
            
#         datadir = "../../mead/data/PhraseMead_"+np+"/"
#         FormatOutputMead(datadir, rate, R)
#         Survey.WriteTASummary(excelfile, datadir)
#          
#         datadir = "../../mead/data/PhraseMeadMMR_"+np+"/"
#         FormatOutputMeadMMR(datadir, rate, R)
#         Survey.WriteTASummary(excelfile, datadir)
  
#         datadir = "../../mead/data/PhraseMeadLexRankMMR_"+np+"/"
#         FormatOutputMeadMMR(datadir, rate, R)
#         Survey.WriteTASummary(excelfile, datadir)
    
#     for course in ['CS2001', 'CS2610']:
#         datadir = "../../mead/data/"+course+"_PhraseMead/"
#         FormatOutputMead(datadir, rate, R)