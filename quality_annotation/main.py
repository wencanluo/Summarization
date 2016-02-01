import fio
from nltk.metrics.agreement import AnnotationTask
import numpy as np
from metric import Metric

def get_QWkappa(input):
    head,body = fio.ReadMatrix(input, True)
    
    metric = Metric()
    
    data = {}
    
    for i,row in enumerate(body):
        for coder, label in enumerate(row):
            if label == 'a': label = '0'
            label = int(label)
            
            if head[coder] not in data:
                data[ head[coder] ] = []
            data[ head[coder] ].append(label)
    
    print 'annototor 1', '\t','annototor 2', '\t', 'accuracy', '\t', 'kappa', '\t', 'QWkappa'
    print head[0], '\t', head[1], '\t', metric.accuracy(data[head[0]], data[head[1]]), '\t', metric.kappa(data[head[0]], data[head[1]]), '\t', metric.QWkappa(data[head[0]], data[head[1]])
    print head[0], '\t', head[2], '\t', metric.accuracy(data[head[0]], data[head[2]]), '\t', metric.kappa(data[head[0]], data[head[2]]), '\t', metric.QWkappa(data[head[0]], data[head[2]])
    print head[1], '\t', head[2], '\t', metric.accuracy(data[head[1]], data[head[2]]), '\t', metric.kappa(data[head[1]], data[head[2]]), '\t', metric.QWkappa(data[head[1]], data[head[2]])
    print '', '\t', 'Average', '\t', np.mean([metric.accuracy(data[head[0]], data[head[1]]), metric.accuracy(data[head[0]], data[head[2]]), metric.accuracy(data[head[1]], data[head[2]])]), '\t',\
        np.mean([metric.kappa(data[head[0]], data[head[1]]), metric.kappa(data[head[0]], data[head[2]]), metric.kappa(data[head[1]], data[head[2]])]), '\t',\
        np.mean([metric.QWkappa(data[head[0]], data[head[1]]), metric.QWkappa(data[head[0]], data[head[2]]), metric.QWkappa(data[head[1]], data[head[2]])])
    
    print metric.confusion_matrix(data[head[0]], data[head[1]])
    
    return 0
    
def get_kappa(input):
    head,body = fio.ReadMatrix(input, True)
    
    data = []
    for i,row in enumerate(body):
        for coder, label in enumerate(row):
            if label == 'a': label = '0'
            data.append((head[coder], i, label))
    
    task = AnnotationTask(data)
    
    print head[0], head[1], task.kappa_pairwise(head[0], head[1])
    print head[0], head[2], task.kappa_pairwise(head[0], head[2])
    print head[1], head[2], task.kappa_pairwise(head[1], head[2])
    return task.kappa()
    
if __name__ == '__main__':
    #input = '../data/quality_annotation/quality_first_coding.txt'
    #input = '../data/quality_annotation/quality_second_coding.txt'
    input = '../data/quality_annotation/quality_third_coding.txt'
    
    #print get_kappa(input)
    print get_QWkappa(input)
    