import ml_metrics as metrics
from sklearn import cross_validation

class Metric:
    def __init__(self):
        pass

    def cv_accuracy(self, labels, predicts, fold=10):
        assert(len(labels) == len(predicts))
        N = len(labels)
        
        metrics = []
        cv = cross_validation.ShuffleSplit(N, fold)
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
    
    def cv_kappa(self, labels, predicts, fold=10):
        assert(len(labels) == len(predicts))
        N = len(labels)
        
        metrics = []
        cv = cross_validation.ShuffleSplit(N, fold)
        for _, test in cv:
            fold_lables = [labels[i] for i in test]
            fold_predicts = [predicts[i] for i in test]
            metric = self.kappa(fold_lables, fold_predicts)
            metrics.append(metric)
        
        return metrics
    
    def kappa(self, labels, predicts):
        return metrics.kappa(labels, predicts)
    
    def cv_QWkappa(self, labels, predicts, fold=10):
        assert(len(labels) == len(predicts))
        N = len(labels)
        
        metrics = []
        cv = cross_validation.ShuffleSplit(N, fold)
        for _, test in cv:
            fold_lables = [labels[i] for i in test]
            fold_predicts = [predicts[i] for i in test]
            metric = self.QWkappa(fold_lables, fold_predicts)
            metrics.append(metric)
        
        return metrics
    
    def QWkappa(self, labels, predicts):
        return metrics.quadratic_weighted_kappa(labels, predicts)
    
if __name__ == '__main__':
    metric = Metric()
    print metric.accuracy([0, 1, 1], [1, 1, 1])
    print metric.kappa([0, 1, 1], [1, 1, 1])
    