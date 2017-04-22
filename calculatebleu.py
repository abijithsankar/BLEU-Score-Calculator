import sys
import codecs
import os
from collections import OrderedDict
import math
import operator

def loadDataFiles(candidateFilePath,refPath):
    candidateFile = codecs.open(candidateFilePath,'r','utf-8')
    candidateData = candidateFile.readlines()
    referenceData = []
    if '.txt' in refPath:
        refFile = codecs.open(refPath,'r','utf-8')
        referenceData.append(refFile.readlines())
    else:
        for root,dirs,files in os.walk(refPath):
            for f in files:
                refFile = codecs.open(os.path.join(root,f),'r','utf-8')
                referenceData.append(refFile.readlines())
    return candidateData,referenceData
        
def findBleu(candidateData,refData):
    precisionValues = []
    for n in range(4):
        precision,brevityPenalty = getNgramMetric(candidateData,refData,n+1)
        precisionValues.append(precision)
    bleuScore = findGM(precisionValues) * brevityPenalty
    return bleuScore

def getNgramMetric(candidateData,refData,n):
    clippedCount = 0
    totalCount = 0
    brevityNum = 0
    brevityDen = 0
    for ci in range(len(candidateData)):
        refLength=[]
        refCounts = []
        for ref in refData:
            refSentence = ref[ci]
            refDict = OrderedDict()
            refTokens = refSentence.strip().split()
            refLength.append(len(refTokens))
            refNgramLength = len(refTokens)-n+1
            for i in range(refNgramLength):
               refNGram = ' '.join(refTokens[i:i+n]).lower()
               if refNGram in refDict.keys():
                   refDict[refNGram] +=1
               else:
                   refDict[refNGram] = 1
            refCounts.append(refDict)
        
        candSentence = candidateData[ci]
        candDict = OrderedDict()
        candTokens = candSentence.strip().split()
        candNgramLength = len(candTokens)-n+1
        for i in range(0,candNgramLength):
            candNGram = ' '.join(candTokens[i:i+n]).lower()
            if candNGram in candDict:
                candDict[candNGram] += 1
            else:
                candDict[candNGram] = 1
        
        clippedCount += clip(candDict,refCounts)
        totalCount += candNgramLength
        brevityNum += findBestLength(refLength,len(candTokens)) 
        brevityDen += len(candTokens)
    if clippedCount == 0:
        precision = 0
    else:
        precision = float(clippedCount)/totalCount
    brevityPenalty = getBrevityPenalty(brevityNum,brevityDen)
    return precision,brevityPenalty  
            
           

def clip(candDict,refCounts):
    clipCount = 0
    for key in candDict.keys():
        tokenCount = candDict[key]
        countMax = 0
        for item in refCounts:
            if key in item:
                countMax = max(countMax,item[key])
        tokenCount = min(tokenCount,countMax)
        clipCount += tokenCount
    return clipCount
    
def findBestLength(refLength,candTokenLength):
    closest = abs(candTokenLength-refLength[0])
    bestMatch = refLength[0]
    for item in refLength:
        if abs(candTokenLength-item) < closest:
            closest = abs(candTokenLength-item)
            bestMatch = item
    return bestMatch

def getBrevityPenalty(brevityNum,brevityDen):
    if brevityDen > brevityNum:
        brevityPenalty = 1
    else:
        brevityPenalty = math.exp(1-(float(brevityNum)/brevityDen))
    return brevityPenalty
    
def findGM(precisionValues):
    return (reduce(operator.mul,precisionValues)) ** (1.0/len(precisionValues))

    
          
    
def main(candidateFilePath,refPath):
    candidateData,refData= loadDataFiles(candidateFilePath,refPath)
    bleuScore = findBleu(candidateData,refData)
    print bleuScore
    f = open('bleu_out.txt','w')
    f.write(str(bleuScore))
    f.close()
    
main(sys.argv[1],sys.argv[2])