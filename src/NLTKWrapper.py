#!/usr/bin/env python

import nltk
import nltk.data
import porter

def splitSentence(paragraph):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(paragraph)
  
def wordtokenizer(s, punct = True):
    if punct:
        return nltk.wordpunct_tokenize(s)
    else:
        return nltk.word_tokenize(s)

def getNgram(sentence, n):
    #n is the number of grams, such as 1 means unigram
    ngrams = []
    
    #tokens = summary.split()
    tokens = wordtokenizer(sentence)
    N = len(tokens)
    for i in range(N):
        if i+n > N: continue
        ngram = tokens[i:i+n]
        ngrams.append(" ".join(ngram))
    return ngrams


if __name__ == '__main__':
    print splitSentence("[1] I love you. [2] Sent 2. [3] sentence 3")