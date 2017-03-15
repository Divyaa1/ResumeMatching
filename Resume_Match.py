#!usr/bin/python

from __future__ import division
import re, codecs, string, nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import *
from pyPdf import PdfFileReader

#In this function, I read the resume file. I expect it to be a PDF version. 
#Further read the text content line by line. Check for unicode characters
#I was getting some unicode character encoding error, so used ascii ignore
def readMyResume(pdf_file_path, isJDFile):
    with open(pdf_file_path) as f:
        pdf_reader = PdfFileReader(f)
        content = "\n".join(page.extractText().strip() for page in pdf_reader.pages)
        content = ' '.join(content.split())        
        content = content.encode('ascii', 'ignore')
        content = unicode(content.strip(codecs.BOM_UTF8), 'utf-8')
    return cleanText(content, isJDFile)

#Here, I read the job description file. I expect it to be in .txt format.
#Same steps that I did while reading resume file
def readJobDescription(jobDescription_file_path, isJDFile):
    with open(jobDescription_file_path) as f:
        jobDescription = ' '.join(line.strip() for line in f)
    jobDescription = unicode(jobDescription.strip(codecs.BOM_UTF8), 'utf-8')
    jobDescription = jobDescription.encode('ascii', 'ignore')
    return cleanText(jobDescription, isJDFile)
    
#This is the function where I do the basic text cleaning    
def cleanText(text, isJDFile):
    #convert text to lowercase
    cleanedStr = str(text).lower()
    #Remove web addresses
    cleanedStr = re.sub(r'(http://\S*)', '', cleanedStr)
    cleanedStr = re.sub(r'(https://\S*)', '', cleanedStr)
    #Remove email addresses
    cleanedStr = re.sub('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\S*)', '', cleanedStr)
    #Some words have slashes which need to be cleaned
    cleanedStr = re.sub('/', ' ', cleanedStr)
    cleanedStr = re.sub(';', ' ', cleanedStr)
    cleanedStr = re.sub(':', ' ', cleanedStr)
    cleanedStr = re.sub('\.', ' ', cleanedStr)
    cleanedStr = re.sub(',', ' ', cleanedStr)
    cleanedStr = re.sub('-', ' ', cleanedStr)
    #Remove punctuations
    exclude = set(string.punctuation)
    cleanedStr = ''.join(ch for ch in cleanedStr if ch not in exclude)
    #Remove numbers/digits
    cleanedStr = re.sub('\d', '', cleanedStr)
    #go to stemming and stop word removal function
    return stemAndRemoveStopWords(cleanedStr, isJDFile)

#This function removes first removes the stop words, then lemmatizes and stems a word
#I am using Lancaster Stemmer for stemming and WordNetTokenizer for lemmatization
def stemAndRemoveStopWords(txtstr, isJDFile):
    stemmedWordsDict = {}
    tokens = txtstr.split()
    stopWordsList = []
    stopWordsList = [line.strip() for line in open("stopWords.txt", 'r')]
    cleanStr = ""
    for t in tokens:
        if t in stopWordsList or len(t)<=1:
            continue
        else:
            cleanStr = cleanStr + " " + t
    cleanStr = cleanStr.strip()

    #Using lemmatization
    lemma = nltk.wordnet.WordNetLemmatizer()
    cleanedStr = " ".join([lemma.lemmatize(s) for s in cleanStr.split(" ") ] )  

   #using stemming
#    cleanedStr = " ".join([PorterStemmer().stem(s) for s in cleanedStr.split(" ")]) 
#    cleanedStr = " ".join([SnowballStemmer("porter").stem(s) for s in cleanedStr.split(" ")])  
    cleanedStr = " ".join([LancasterStemmer().stem(s) for s in cleanedStr.split(" ")])  
    if isJDFile == 'Y':
        for s in cleanStr.split(" "):
            stemmedWordsDict[PorterStemmer().stem(s)] =  s
        return cleanedStr, stemmedWordsDict
    else:
        return cleanedStr

#This function calculates the percent match pf resume and job description considering matched words
def calculatePercentMatch(resumeContent, jobDescription, stemmedWordsDict):
    #Initializing all lists used in this function
    resumeText = [] 
    jdText = []
    matchedString = []
    matchedList = []
    unMatchedList = []

    #Tokenize resume content and append to list
    for word in resumeContent.split():
        if not word in resumeText:
            resumeText.append(word)
    #Tokenize job description content and append to list
    for word in jobDescription.split():
        if not word in jdText:
            jdText.append(word)
    #Match the content in both lists        
    for val in jdText:
        #if match exists, append to matched list and show original for stemmed word
        if val in resumeText:
            matchedString.append(str(val))
            for key, value in stemmedWordsDict.items():
                if key == val:
                    matchedList.append(value)
        #if match does not exist, append to unMatched list and show original for stemmed word
        else:
            for key, value in stemmedWordsDict.items():
                if key == val:
                    unMatchedList.append(value)

    #Calculate the percentage match 
    percentMatch = (len(matchedString)/len(jdText))*100
    print '\n'
    print "There is a %f percent match in your resume and the job description" %percentMatch
    print '\n'
    print "The matched words in your resume are:"
    print matchedList
    print '\n'
    if(percentMatch < 70):
        print "You may want to add a few terms from these into your resume to improve the match"
        print unMatchedList
    
    
#Calling the main function
if __name__ == '__main__':
    #path for resume file
    pdf_file_path = "Resume_FileName.pdf"
    #path for job description file
    jobDescription_file_path = "JobDescription.txt"
    #read resume file
    resumeContent = readMyResume(pdf_file_path, isJDFile = 'N')
    #read job description file    
    jobDescription, stemmedWordsDict = readJobDescription(jobDescription_file_path, isJDFile = 'Y')
    #Calculate the percentage match 
    calculatePercentMatch(resumeContent, jobDescription, stemmedWordsDict)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    