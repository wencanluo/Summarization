import os

if __name__ == '__main__':
    #     . Prepare Senna Input (CourseMirrorSurvey.py)
    os.system('python CourseMirrorSurvey.py')
    
    #     . Get Senna Output
    os.system('runSennaCourseMirror.bat')
    
    #     . extract phrases (CourseMirror_phrasebasedShallowSummary.py)
    os.system('python CourseMirror_phrasebasedShallowSummary.py')
    
    #     . get PhraseMead input (CourseMirror_MeadPhrase.py)
    os.system('python CourseMirror_MeadPhrase.py')
    
    #     . get PhraseMead output
    os.system('pause')
    
    #     . get LSA results (CourseMirrorphrase2phraseSimilarity.java)
    #os.system('pause')
    
    #     . get ClusterARank (CourseMirror_phraseClusteringbasedShallowSummaryKmedoid-New-Malformed-LexRank.py)
    os.system("python CourseMirror_phraseClusteringbasedShallowSummaryKmedoid-New-Malformed-LexRank.py")
    
    #     . submit Summary (SummaryUpdate.py)
    
    
    #     . Print summary(PrintClusterRankSummary PostProcess.py)