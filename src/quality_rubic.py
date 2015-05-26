import sys, fio
import QualityPrediction
import Survey
import NLTKWrapper
from collections import defaultdict
import quality_binary_model

class_label = '@class@'

def rubric_baseline(excelfile, prob, titledir, output):
    head, types, data = quality_binary_model.getBinaryFeatures(excelfile, prob, titledir, output)
    
    class_index = head.index(class_label)
    
    features = [head.index(key) for key in head if key != class_label]
    
    NonZero = head.index('NoneZero')
    Content = head.index('Content')
    OrgAssign = head.index('OrgAssign')
    Title = head.index('Title')
    ProbBinary = head.index('ProbBinary')

    new_head = ['True', 'Predict']
    new_body = []
    
    for row in data:
        new_row = []
        label = row[class_index]
        
        new_row.append(label)
        
        predict = None
        
        if (not row[NonZero]) or (not row[Content] and not row[OrgAssign]):
            predict = '0.0'
        if (row[NonZero] and not row[Content] and row[OrgAssign]) or (row[NonZero] and row[Content] and not row[ProbBinary] and row[Title]):
            predict = '1.0'
        if (row[NonZero] and row[Content] and not row[ProbBinary] and not row[Title]):
            predict = '2.0'
        if (row[NonZero] and row[Content] and row[ProbBinary]):
            predict = '3.0'
        new_row.append(predict)
        new_body.append(new_row)
    
    fio.WriteMatrix(output, new_body, new_head)

if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    speciteller_datadir = "../data/speciteller/"
    prob = "../data/MP.prob"
    titledir = "E:/Dropbox/reflection project_LRDC/250 Sp11 CLIC All Lecs .2G/titles/"
    
#     wekafile = "../data/weka/quality_binary_model.arff"
#     WriteQuality2Weka_Binary(excelfile, prob, titledir, wekafile)
    
    output = "../data/weka/quality_rubric.label"
    rubric_baseline(excelfile, prob, titledir, output)