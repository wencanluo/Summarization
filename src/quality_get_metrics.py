import fio
import os
from metric import Metric
from __builtin__ import file
from collections import defaultdict

def load_label(labelfile):
    header, body = fio.ReadMatrix(labelfile, hasHead=True)
    label_index = header.index('True')
    predict_index = header.index('Predict')
    if 'fold' in header:
        fold_index = header.index('fold')
    else:
        fold_index = -1
    
    labels = [int(float(row[label_index])) for row in body]
    predicts = [int(float(row[predict_index])) for row in body]
    if fold_index != -1:
        folds = [int(float(row[fold_index])) for row in body]
    else:
        folds = None
    
    return labels, predicts, folds
    
def get_metrics_cv(datadir, files):
    metric = Metric()
    
    _, _, folds = load_label(datadir + files[0])
    
    body = []
    for file in files:
        labels, predicts, _ = load_label(datadir + file)
        row = [file]
        row += metric.cv_accuracy(labels, predicts, folds)
        row += metric.cv_kappa(labels, predicts, folds)
        row += metric.cv_QWkappa(labels, predicts, folds)
        body.append(row)
    
    output = datadir+'H1_p.txt'
    print output
    fio.WriteMatrix(output, body, header=None)
    
def get_metrics_H1(datadir):
    files = ['quality_WC_Unigram.label',
         'quality_WC_Unigam_NonZero.label',
         'quality_WC_Unigam_Content.label',
         'quality_WC_Unigam_OrgAssign.label',
         'quality_WC_Unigam_Speciteller.label',
         'quality_WC_Unigam_Title.label',
         'quality_DT.label',
         'quality_New.label',
         #'quality_New-Title.label',
         'quality_firstnode.label'
         ] 
        
    metric = Metric()
    
    body = []
    for file in files:
        labels, predicts, _ = load_label(datadir + file)
        row = [file]
        row.append(metric.accuracy(labels, predicts))
        row.append(metric.kappa(labels, predicts))
        row.append(metric.QWkappa(labels, predicts))
        body.append(row)
    
    output = datadir+'H1.txt'
    print output
    fio.WriteMatrix(output, body, header=None)
    
    #get_metrics_cv(datadir, files)

def fix_firstnode(input, zero_file, output):
    header, body = fio.ReadMatrix(input, hasHead=True)
    label_index = header.index('True')
    predict_index = header.index('Predict')
    
    labels = [row[label_index] for row in body]
    predicts = [row[predict_index] for row in body]
    
    zero_labels = fio.LoadList(zero_file)
    
    assert(len(predicts) == len(zero_labels))
    
    head = ['True', 'Predict']
    body = []
    for i, (label, predict) in enumerate(zip(labels, predicts)):
        if zero_labels[i] == '0':
            predict = '0.0'
        
        row = [label, predict]
        body.append(row)
    
    fio.WriteMatrix(output, body, head)
    
def get_metrics_H1_CV(datadir):
    metric = Metric()
    
    folds = range(0, 10)
    
    #fix firstnode
    feature = 'quality_rubric_firstnode_'
    feature_fixed = 'quality_rubric_firstnode_fixed_'
    
    for fold in folds:
        input = datadir + feature + str(fold)+'_test.label'
        zero_file = datadir + feature + str(fold)+'_test_0.txt'
        output = datadir + feature_fixed + str(fold)+'_test.label'
        fix_firstnode(input, zero_file, output)
         
    body = []
    for feature in ['quality_WC_Unigram_', 
                    'quality_WC_Unigam_NonZero_', 
                    'quality_WC_Unigam_Content_', 
                    'quality_WC_Unigam_OrgAssign_', 
                    'quality_WC_Unigam_Speciteller_', 
                    'quality_WC_Unigam_Title_',
                    'quality_rubric_',
                    'quality_rubric_firstnode_fixed_',
                    'quality_DT_',
                    ]:
        for fold in folds:
            file = feature + str(fold)+'_test.label'
            print file
            
            labels, predicts, _ = load_label(datadir + file)
            row = [file]
            row.append(metric.accuracy(labels, predicts))
            row.append(metric.kappa(labels, predicts))
            row.append(metric.QWkappa(labels, predicts))
            body.append(row)
    
    output = datadir+'H1_cv.txt'
    print output
    fio.WriteMatrix(output, body, header=None)  
    
def get_metrics_H2a(datadir):
    metric = Metric()
    
    lectures = range(1, 24)
    
    #fix firstnode
    feature = 'quality_CrossLecture_Rubric_firstnode_'
    feature_fixed = 'quality_CrossLecture_Rubric_firstnode_fixed_'
    
    for fold in lectures:
        input = datadir + feature + str(fold)+'_test.label'
        zero_file = datadir + feature + str(fold)+'_test_0.txt'
        output = datadir + feature_fixed + str(fold)+'_test.label'
        fix_firstnode(input, zero_file, output)
        
    body = []
    for feature in [
                    'quality_CrossLecture_WC_Unigram_', 
                    'quality_CrossLecture_Rubric_', 
                    'quality_CrossLecture_Rubric_firstnode_fixed_',
                    'quality_CrossLecture_DT_', 
                    ]:
        for lecture in lectures:
            file = feature + str(lecture)+'_test.label'
            print file
            
            labels, predicts, _ = load_label(datadir + file)
            row = [file]
            row.append(metric.accuracy(labels, predicts))
            row.append(metric.kappa(labels, predicts))
            row.append(metric.QWkappa(labels, predicts))
            body.append(row)
    
    output = datadir+'H2_crosslecture.txt'
    print output
    fio.WriteMatrix(output, body, header=None)  

def get_metrics_H2b(datadir):
    metric = Metric()
    
    lectures = range(1, 9)
    
    feature = 'quality_CrossTopic_Rubric_firstnode_'
    feature_fixed = 'quality_CrossTopic_Rubric_firstnode_fixed_'
    
    for fold in lectures:
        input = datadir + feature + str(fold)+'_test.label'
        zero_file = datadir + feature + str(fold)+'_test_0.txt'
        output = datadir + feature_fixed + str(fold)+'_test.label'
        fix_firstnode(input, zero_file, output)
        
    body = []
    for feature in [
                    'quality_CrossTopic_WC_Unigram_', 
                    'quality_CrossTopic_Rubric_', 
                    'quality_CrossTopic_Rubric_firstnode_fixed_',
                    'quality_CrossTopic_DT_', 
                    ]:
        for lecture in lectures:
            file = feature + str(lecture)+'_test.label'
            print file
            
            labels, predicts, _ = load_label(datadir + file)
            row = [file]
            row.append(metric.accuracy(labels, predicts))
            row.append(metric.kappa(labels, predicts))
            row.append(metric.QWkappa(labels, predicts))
            body.append(row)
    
    output = datadir+'H2b.txt'
    print output
    fio.WriteMatrix(output, body, header=None)  

def get_metrics_H2c(datadir):
    metric = Metric()
    
    feature = 'quality_CrossCourse_Rubric_firstnode'
    feature_fixed = 'quality_CrossCourse_Rubric_firstnode_fixed'
    
    input = datadir + feature +'_test.label'
    zero_file = datadir + feature +'_test_0.txt'
    output = datadir + feature_fixed +'_test.label'
    fix_firstnode(input, zero_file, output)
    
    body = []
    for feature in [
                    'quality_CrossCourse_WC_Unigram',
                    'quality_CrossCourse_Rubric',
                    'quality_CrossCourse_Rubric_firstnode_fixed',
                    'quality_CrossCourse_DT', 
                    ]:
        file = feature+'_test.label'
        print file
        
        labels, predicts, _ = load_label(datadir + file)
        row = [file]
        row.append(metric.accuracy(labels, predicts))
        row.append(metric.kappa(labels, predicts))
        row.append(metric.QWkappa(labels, predicts))
        body.append(row)
    
    output = datadir+'H2c.txt'
    print output
    fio.WriteMatrix(output, body, header=None) 
 
def get_metrics_H0(datadir):
    metric = Metric()

    body = []
    for feature in ['quality_rubric', 'quality_binary_model', 'quality_New', 'quality_firstnode']:
        file = feature+'.label'
        print file

        labels, predicts, _ = load_label(datadir + file)
        fio.WriteMatrix(datadir + file + '.cm', metric.confusion_matrix(labels, predicts), None)
        
        row = [file]
        row.append(metric.accuracy(labels, predicts))
        row.append(metric.kappa(labels, predicts))
        row.append(metric.QWkappa(labels, predicts))
#         row += metric.cv_accuracy(labels, predicts)
#         row += metric.cv_kappa(labels, predicts)
#         row += metric.cv_QWkappa(labels, predicts)
        body.append(row)
    
    output = datadir+'H0.txt'
    print output
    fio.WriteMatrix(output, body, header=None) 

def get_metrics_NewCourse(datadir):
    files = ['DT.txt',
         'DT_NoneZero.txt',
         'Rubric.txt',
         'Rubric_NoneZero.txt',
         ] 
        
    metric = Metric()
    
    body = []
    for file in files:
        labels, predicts, _ = load_label(datadir + file)
        row = [file]
        row.append(metric.accuracy(labels, predicts))
        row.append(metric.kappa(labels, predicts))
        row.append(metric.QWkappa(labels, predicts))
        body.append(row)
    
    output = datadir+'H_NewCourse.txt'
    print output
    fio.WriteMatrix(output, body, header=None)

def get_distrubtion():
    
    files = ['DT.txt',
         'DT_NoneZero.txt',
         'Rubric.txt',
         'Rubric_NoneZero.txt',
         ] 
    
    dicts = []
    
    for file in files:
        labels, predicts, _ = load_label(datadir + file)
    
        dict = defaultdict(int)
        for label in predicts:
            dict[label] += 1
        
        dicts.append(dict)
    
    for dict in dicts:
        for label in range(4):
            print dict[label], '\t', 
        print
                
if __name__ == '__main__':
    datadir = '../data/weka/'
    
    get_metrics_H1_CV(datadir)
#     get_metrics_H1(datadir)
#     get_metrics_H2a(datadir)
#     get_metrics_H2b(datadir)
    #get_metrics_H2c(datadir)
    #get_metrics_NewCourse(datadir)
    
    #get_distrubtion()