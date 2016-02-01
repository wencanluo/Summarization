#https://github.com/benhamner/Metrics/tree/master/Python/ml_metrics

import ml_metrics as metrics
from sklearn import cross_validation

class Metric:
    def __init__(self):
        pass
    
    def get_folders(self, folds):
        N = sorted(set(folds))
        
        for fold in N:
            train = []
            test = []
            
            for i, x in enumerate(folds):
                if x == fold:
                    test.append(i)
                else:
                    train.append(i)
            yield train, test
        
    def cv_accuracy(self, labels, predicts, folds):
        assert(len(labels) == len(predicts))
        N = len(labels)
        
        metrics = []
        cv = self.get_folders(folds)
        
        for _, test in cv:
            fold_lables = [labels[i] for i in test]
            fold_predicts = [predicts[i] for i in test]
            metric = self.accuracy(fold_lables, fold_predicts)
            metrics.append(metric)
        
        return metrics
    
    def accuracy(self, labels, predicts):
        assert(len(labels) == len(predicts))
        N = len(labels)
        
        hit = 0.0
        
        for label, predict in zip(labels, predicts):
            if label == predict:
                hit += 1
        
        return hit/N
    
    def cv_kappa(self, labels, predicts, folds):
        assert(len(labels) == len(predicts))
        N = len(labels)
        
        metrics = []
        cv = self.get_folders(folds)
        
        for _, test in cv:
            fold_lables = [labels[i] for i in test]
            fold_predicts = [predicts[i] for i in test]
            metric = self.kappa(fold_lables, fold_predicts)
            metrics.append(metric)
        
        return metrics
    
    def kappa(self, labels, predicts):
        return metrics.kappa(labels, predicts)
    
    def cv_QWkappa(self, labels, predicts, folds):
        assert(len(labels) == len(predicts))
        N = len(labels)
        
        metrics = []
        cv = self.get_folders(folds)
        for _, test in cv:
            fold_lables = [labels[i] for i in test]
            fold_predicts = [predicts[i] for i in test]
            metric = self.QWkappa(fold_lables, fold_predicts)
            metrics.append(metric)
        
        return metrics
    
    def QWkappa(self, labels, predicts):
        return metrics.quadratic_weighted_kappa(labels, predicts)
    
    def confusion_matrix(self, labels, predicts):
        return metrics.confusion_matrix(labels, predicts)
        
if __name__ == '__main__':
    metric = Metric()
    #print metric.accuracy([0, 1, 1], [1, 1, 1])
    #print metric.kappa([0, 1, 1], [1, 1, 1])
    #print metric.confusion_matrix([1, 2, 3], [1, 1, 1])
    
    cv = cross_validation.ShuffleSplit(100, 10, random_state=0)
    for _, test in cv:
        print test