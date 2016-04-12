import sys
import re
import fio
import xml.etree.ElementTree as ET
from collections import defaultdict
from Survey import *
import random
import NLTKWrapper
import SennaParser
import porter

prompt_dict = {'POI':'q1',
               'MP':'q2'
               }
                 
def getShallowSummary(excelfile, folder, keyhphrasedir, K=30):
    sheets = range(0,25)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        for type in ['POI', 'MP']:#, 'LP'
            print excelfile, sheet, type
            
            path = folder + str(week)+ '/'
            filename = path + type + '.summary'
            
            keyphrasefilename = keyhphrasedir + str(week) + "." + type + '.key'
            if not fio.IsExist(keyphrasefilename): continue
            
            fio.NewPath(path)
            keyphrases = [line.strip() for line in fio.ReadFile(keyphrasefilename)]

            Summary = []
            
            total_word = 0
            word_count = 0
            for phrase in keyphrases:
                if phrase in Summary: continue
                
                word_count = len(phrase.split())
                total_word = total_word + word_count
                #if len(Summary) +1 <= K:
                
                if total_word <= K:
                    Summary.append(phrase)
                else:
                    total_word = total_word - word_count
            
            fio.SaveList(Summary, filename)
                        
def ShallowSummary(excelfile, datadir, keyhphrasedir, K=30):
    getShallowSummary(excelfile, datadir, keyhphrasedir, K)
    #WriteTASummary(excelfile, datadir)
        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    keyhphrasedir = "../../Maui1.2/data/IE256/"
    datadir = "../../mead/data/IE256_C16/keyphrase/"  
    
    fio.DeleteFolder(datadir)
    ShallowSummary(excelfile, datadir, keyhphrasedir, K=16)    