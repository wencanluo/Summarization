import sys, fio
import QualityPrediction
import Survey
import NLTKWrapper
from collections import defaultdict

class_label = '@class@'
import QualityPrediction
 
def first_node_baseline(excelfile, prob, titledir, output):
    head, types, data = QualityPrediction.get_Quality_RubricFeatures(excelfile, prob, titledir)
    
    class_index = head.index(class_label)
    
    NonZero = head.index('NoneZero')
    
    new_head = ['True', 'Predict', 'fold']
    new_body = []
    
    for row in data:
        label = row[class_index]
        
        if not row[NonZero]:
            new_row = []
            new_row.append(label)
            new_row.append('0.0')
            new_row.append('0')
            new_body.append(new_row)
    
    fio.WriteMatrix(output + '_0.label', new_body, new_head)
    
    head.pop(NonZero)
    types.pop(NonZero)
    
    new_body = []
    for row in data:
        if row[NonZero]:
            row.pop(NonZero)
            new_body.append(row)
    fio.ArffWriter(output, head, types, "Quality", new_body)

        
if __name__ == '__main__':
    excelfile = "../data/2011Spring.xls"
    speciteller_datadir = "../data/speciteller/"
    prob = "../data/MP.prob"
    titledir = "E:/Dropbox/reflection project_LRDC/250 Sp11 CLIC All Lecs .2G/titles/"
    
#     wekafile = "../data/weka/quality_binary_model.arff"
#     WriteQuality2Weka_Binary(excelfile, prob, titledir, wekafile)
    
    output = "../data/weka/quality_firstnode.arff"
    first_node_baseline(excelfile, prob, titledir, output)