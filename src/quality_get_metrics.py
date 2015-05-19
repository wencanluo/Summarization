import fio
from metric import Metric
from __builtin__ import file

def load_label(labelfile):
    header, body = fio.ReadMatrix(labelfile, hasHead=True)
    label_index = header.index('True')
    predict_index = header.index('Predict')
    
    labels = [int(float(row[label_index])) for row in body]
    predicts = [int(float(row[predict_index])) for row in body]
    
    return labels, predicts
    
def get_metrics_cv(datadir, files):
    metric = Metric()
    
    body = []
    for file in files:
        labels, predicts = load_label(datadir + file)
        row = [file]
        row += metric.cv_accuracy(labels, predicts)
        row += metric.cv_kappa(labels, predicts)
        row += metric.cv_QWkappa(labels, predicts)
        body.append(row)
    
    output = datadir+'H1.txt'
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
         ] 
        
    metric = Metric()
    
    body = []
    for file in files:
        labels, predicts = load_label(datadir + file)
        row = [file]
        row.append(metric.accuracy(labels, predicts))
        row.append(metric.kappa(labels, predicts))
        row.append(metric.QWkappa(labels, predicts))
        body.append(row)
    
    output = datadir+'H1.txt'
    print output
    fio.WriteMatrix(output, body, header=None)    

def get_metrics_H2(datadir):
    metric = Metric()
    
    lectures = range(1, 24)
    
    body = []
    for feature in ['quality_CrossLecture_DT_', 'quality_CrossLecture_WC_Unigram_', 'quality_CrossLecture_New_']:
        for lecture in lectures:
            file = feature + str(lecture)+'_test.label'
            print file
            
            labels, predicts = load_label(datadir + file)
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
    
    body = []
    for feature in ['quality_CrossTopic_DT_', 'quality_CrossTopic_WC_Unigram_', 'quality_CrossTopic_New_']:
        for lecture in lectures:
            file = feature + str(lecture)+'_test.label'
            print file
            
            labels, predicts = load_label(datadir + file)
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

    body = []
    for feature in ['quality_CrossCourse_DT_test', 'quality_CrossCourse_WC_Unigram_test', 'quality_CrossCourse_New_test']:
        file = feature+'.label'
        print file
        
        labels, predicts = load_label(datadir + file)
        row = [file]
        row.append(metric.accuracy(labels, predicts))
        row.append(metric.kappa(labels, predicts))
        row.append(metric.QWkappa(labels, predicts))
        body.append(row)
    
    output = datadir+'H2c.txt'
    print output
    fio.WriteMatrix(output, body, header=None) 
            
if __name__ == '__main__':
    datadir = '../data/weka/'
    
    get_metrics_H2c(datadir)