#https://github.com/belambert/asr_evaluation
#import asr_evaluation

import Transcibe_XML2Excel
import fio

def getWER(path):
    head = ["", "", 600, 800, 1000, 1200, 1400]
    body = []
    for source in ['source1', 'source2', 'source3']:
        for e in [5, 10, 15, 20, 25]:
            row = []
            row.append(source)
            row.append(e)
            
            for s in [600, 800, 1000, 1200, 1400]:
                #out = "annotation_asr_" + str(e) + "_" + str(s) + "_" + source + ".out"
                out = "annotation_norm_asr_" + str(e) + "_" + str(s) + "_" + source + ".out"
                
                lines = fio.ReadFile(path + out)
                wer = lines[-1]
                
                key = wer.find('% (')
                number = wer[len("WER: "): key]
                row.append(number)
        
            body.append(row)
    fio.WriteMatrix(path + "wer_norm_source.txt", body, head)

def SaveUtterances(Utterances, path):
    for id, utterances in Utterances.items():
        fio.SaveList(utterances, path + "_" + id + ".txt", " ")
    
if __name__ == '__main__':
    #get reference text
    path = "E:/project/Audio/"
    
#     utterances = Transcibe_XML2Excel.getUtterance(path, "ref.xml")
#     output = "ref"
#     SaveUtterances(utterances, path + output)
#      
#     #get ASR text        
#     for e in [5, 10, 15, 20, 25]: 
#         for s in [600, 800, 1000, 1200, 1400]:
#             #xml = "annotation_asr_" + str(e) + "_" + str(s) + ".xml"
#             xml = "annotation_norm_asr_" + str(e) + "_" + str(s) + ".xml"
#             print xml
#                 
#             utterances = Transcibe_XML2Excel.getUtterance(path, xml)
#             #output = "annotation_asr_" + str(e) + "_" + str(s)
#             output = "annotation_norm_asr_" + str(e) + "_" + str(s)
#             #fio.SaveList(utterances, path + output, " ")
#             SaveUtterances(utterances, path + output)
    
    #get WER
    getWER(path)
