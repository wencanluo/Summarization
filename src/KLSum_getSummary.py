import sys
import re
import fio
from collections import defaultdict
from Survey import *
import random
import NLTKWrapper
import xml.etree.ElementTree as ET

import os
import SumBasic_word as SumBasic

KLSUM_EXE = "../../summarizer/src/run_KLSum_word.exe"

def toXMLDocument(filename, xml):
    #format the responses to XMl document, with tokinziation
    #create a XML file
    lines = fio.ReadFile(filename)
    
    #article
    root = ET.Element(tag='article', attrib = {'id':filename})
    root.tail = '\n'
    tree = ET.ElementTree(root)
    
    #title
    title = ET.Element(tag='title')
    title.text = filename
    title.tail = "\n"
    root.append(title)
    
    #body
    body = ET.Element(tag='body')
    title.tail = "\n"
    root.append(body)
    
    #item
    item = ET.Element(tag='item', attrib = {'id':filename})
    item.tail = "\n"
    body.append(item)
    
    #text
    text = ET.Element(tag='text')
    text.tail = "\n"
    item.append(text)
    
    for i, sentence in enumerate(lines):
        
        p = ET.Element(tag='p')
        p.tail = "\n"
        text.append(p)
        
        sentence = sentence.strip()
        sentence_node = ET.Element(tag='sentence', attrib={'id':str(i)})
        sentence_node.tail = "\n"
        p.append(sentence_node)
        plainText = ET.Element(tag='plainText')
        plainText.text = sentence
        plainText.tail = "\n"
        sentence_node.append(plainText)
        
        tokens = sentence.split()
        tokens_node = ET.Element(tag='tokens')
        sentence_node.append(tokens_node)
        
        for j, token in enumerate(tokens):
            node = ET.Element(tag='token', attrib={'id':str(i) + "." + str(j)})
            node.text = token
            node.tail = '\n'
            tokens_node.append(node)
            
    tree.write(xml)
                       
def getShallowSummary(excelfile, folder, K):
    #K is the number of words per points
    header = ['ID', 'Gender', 'Point of Interest', 'Muddiest Point', 'Learning Point']
    summarykey = "Top Answers"
    
    sheets = range(0,12)
    
    for i, sheet in enumerate(sheets):
        week = i + 1
        orig = prData(excelfile, sheet)
        
        for type in ['POI', 'MP', 'LP']:
            print excelfile, sheet, type
            student_summaryList = getStudentResponseList(orig, header, summarykey, type)

            path = folder + str(week)+ '/'
            fio.NewPath(path)
            xlm = path + type + '.xml'
            
            filename = path + type + '.txt'
            fio.SaveList(student_summaryList, filename)
            toXMLDocument(filename, xlm)
            
            summaryfile = path + type + '.summary'
            
            #run the KL
            cmd =  KLSUM_EXE + ' ' + xlm + ' ' + summaryfile
            
            print cmd
            os.system(cmd)
            
                        
def ShallowSummary(excelfile, datadir, K=30):
    getShallowSummary(excelfile, datadir, K)
    WriteTASummary(excelfile, datadir)
        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    
    sennadatadir = "../data/senna/"
        
    datadir = "../../mead/data/C30_KLSum/"  
    fio.DeleteFolder(datadir)
    ShallowSummary(excelfile, datadir, K=30)

    print 'done'
    