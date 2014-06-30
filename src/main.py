from OrigReader import prData
import sys
import re

def load(excelfile, output):
    
    SavedStdOut = sys.stdout
    sys.stdout = open(output, 'w')
    
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    sheets = range(1,15)
    
    for sheet in sheets:
        orig = prData(excelfile, sheet)
        
        for k, inst in enumerate(orig._data):
            value = inst[key].lower().strip()
            
            
   
    sys.stdout = SavedStdOut
          
if __name__ == '__main__':
    excelfile = "E:\Dropbox\reflection project_LRDC"
    luafile = "hindi/src/lua/stimuli.lua"
    
    load(excelfile, output)