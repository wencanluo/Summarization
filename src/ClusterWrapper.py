from Bio.Cluster import * 
#need http://biopython.org/ with numpy >= 9

def KCluster(data, K=2):

    clusterid, error, nfound = kcluster (data, nclusters=K, mask=None, weight=None, transpose=0, npass=1, method='a', dist='e', initialid=None)
    cdata, cmask = clustercentroids(data, mask=None, transpose=0, clusterid=clusterid, method='a')

    return clusterid, cdata

if __name__ == '__main__':
    
    #http://mnemstudio.org/clustering-k-means-example-1.htm
    data = [[1,1],
        [1.5,2],
        [3,4],
        [5,7],
        [3.5,5],
        [4.5,5],
        [3.5,4.5],
    ]
        
    clusterid, cdata = KCluster(data, 2)
    
    print clusterid
    print cdata
    
    print "done"