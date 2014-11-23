import shutil
import fio

def mycopy():
    clusterdir = "../data/np0/"

    for i in range(100, 1000):
        clusterdir2 = "../data/np"+str(i)+"/"
        shutil.copytree(clusterdir, clusterdir2)

if __name__ == '__main__':
    mycopy()