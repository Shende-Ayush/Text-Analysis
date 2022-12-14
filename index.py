
# # After running this cell please restart the Runtime 


# !pip install beautifulsoup4
# !pip install numpy
# !pip install requests
# !pip install spacy
# !pip install trafilatura
# !pip install "urllib3"
# !pip install lxml

from bs4 import BeautifulSoup
import json
import numpy as np
import requests
from requests.models import MissingSchema
import spacy
import trafilatura
from nltk.corpus import stopwords
import nltk
import re
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3, socket
from urllib3.connection import HTTPConnection

"""#Getting Content out from the URL"""

def beautifulsoup_extract_text_fallback(response_content):
    
    '''
    This is a fallback function, so that we can always return a value for text content.
    Even for when both Trafilatura and BeautifulSoup are unable to extract the text from a 
    single URL.
    '''

    # Create the beautifulsoup object:
    # soup = BeautifulSoup(response_content, 'html.parser')
    soup = BeautifulSoup(response_content, "html.parser")
    
    # Finding the text:
    text = soup.find_all(text=True)
  
    # Remove unwanted tag elements:
    cleaned_text = ''
    blacklist = [
        '[document]',
        'noscript',
        'header',
        'html',
        'meta',
        'head', 
        'input',
        'script',
        'style',]

    # Then we will loop over every item in the extract text and make sure that the beautifulsoup4 tag
    # is NOT in the blacklist
    for item in text:
        if item.parent.name not in blacklist:
            cleaned_text += '{} '.format(item)

    # Remove any tab separation and strip the text:
    cleaned_text = cleaned_text.replace('\t', '')
    return cleaned_text.strip()

def extract_text_from_single_web_page(url):

  # HTTPConnection.default_socket_options = ( 
  #     HTTPConnection.default_socket_options + [
  #     (socket.SOL_SOCKET, socket.SO_SNDBUF, 1000000), #1MB in byte
  #     (socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000)
  # ])
  # resp={"status_code":""} 
  try:
    resp = requests.get(url, timeout=5,headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
  except requests.exceptions.ConnectionError:
    # resp.status_code = "Connection refused" 
    return np.nan
  # We will only extract the text from successful requests:
  # print(resp)
  if resp.status_code == 200:
      # print(resp.content)
      return beautifulsoup_extract_text_fallback(resp.content)
  else:
      # This line will handle for any failures in both the Trafilature and BeautifulSoup4 functions:
      return np.nan

"""#Getting Url ID and URLs from input file"""

URL_ID=[]
URL=[]
df = pd.read_excel("InPut_1.xlsx")

for i in range (0,len(df)): 
  print(i)
  temp = list(df.iloc[i])
  URL_ID.append(str(temp[:][0]))
  x=str(temp[1][:])
  if (x[:4]!="http"):
    x="http://"+x
    
  URL.append(x)

print(URL_ID)


print(URL)

"""#syllable_count and syllable_word_count

#word and sentence  counter And Input String

#checking if word is complex or not 

#syllable_count and syllable_word_count

*   syllable_count
*   syllable_word_count
"""

def syllable_and_count(word ,syllable_count,syllable_word_count,complex_word):
    count = 0
    syllable = []
    vowels = "aeiou"
    for i in word:
      if i in vowels:
        syllable.append(i)
        count+=1
    
    if (word[-2:]=="ed") or (word[-2:]=='es'):
      count=-1
    if count<0:
      count = 0
    if count>0:
      syllable_count+=len(set(syllable))
      if len(set(syllable))>=2:
        complex_word+=1
    syllable_word_count+=1

    return (complex_word,syllable_count,syllable_word_count)



"""#creating List for Stop word


# Collecting All Stop Words in as on list



"""

import nltk
nltk.download('stopwords')
stopwords=(stopwords.words('english'))
files_stopwords = ["Stopwords/StopWords_Auditor.txt", 
                   "Stopwords/StopWords_Currencies.txt",
                   "Stopwords/StopWords_DatesandNumbers.txt",
                   "Stopwords/StopWords_Generic.txt",
                   "Stopwords/StopWords_GenericLong.txt",
                   "Stopwords/StopWords_Geographic.txt",
                   "Stopwords/StopWords_Names.txt"]

for i in files_stopwords :
  w=open("{filename}".format(filename=i),'r').read().strip().lower()
  stopwords.extend(w.split())
# stopwords=english_stopwords.extend(stopwords)

stopwords.extend(["./td-block-span12",
                            "/.content",
                            "./td-related-span4",
                            "./block",
                            "./block1",
                            "/.td-pb-row",
                            "/.td-container",  
                            "/.post"])

stopwords=set(stopwords)
len(stopwords)

"""#Negative words"""

negative_words=open("{filename}".format(filename="negative-words.txt"),'r').read().strip().lower()
negative_words=set(negative_words.split())
# print(negative_words)
# print(len(negative_words))

"""#Positive words"""

positive_words=open("{filename}".format(filename="positive-words.txt"),'r').read().strip().lower()
positive_words=set(positive_words.split())
# print(positive_words)
# print(len(positive_words))

# declearing  arrays to store outputs 
POSITIVE_SCORE=[]
NEGATIVE_SCORE=[]
POLARITY_SCORE=[]
SUBJECTIVITY_SCORE=[]
AVG_SENTENCE_LENGTH=[]
PercentageOfComplexWords=[]
FogIndex=[]
AVG_NUMBER_OF_WORDS_PER_SENTENCE=[]
COMPLEX_WORD_COUNT=[]
WORD_COUNT=[]
PERSONAL_PRONOUNS=[]
SYLLABLE_PER_WORD=[]
AVG_WORD_LENGTH=[]

url_no=0
print("iterating through each url in list")
#iterating through each url in list
for url in URL:
  url_no+=1
  print("ongoing URL ====" , url_no)
  doc=""
  #declearing variuable for input string
  input_string=""
  # text_content = [extract_text_from_single_web_page(url) for url in URL]
  print("iterating completed")
  cleaned_text =   extract_text_from_single_web_page(url)
   
  # for cleaned_text in text_content:

  if str(cleaned_text) != 'nan': #cleaning request (text_content) if it has any nan value

    nlp = spacy.load('en_core_web_sm')
    # 1. Create an NLP document with Spacy:
    doc = nlp(cleaned_text)
    input_string=str(doc).lower().strip().split()
    # print("doc=--------->>>>\n",doc)

    input_string= str(doc)
    input_string=input_string.lower().split()
    tokens_without_sw = [word for word in input_string if not word in stopwords] 


    pronounRegex = re.compile(r'\b(I|we|my|ours|(?-i:us))\b',re.I)
    pronouns = pronounRegex.findall(str(doc))

    all_words=0
    negative_word_count = 0
    positive_word_count = 0
    complex_word,syllable_count,syllable_word_count =0,0,0
    number_of_sentences=len(list(doc.sents))

    for i in tokens_without_sw:
      all_words+=1 # word counter

      
      if i in negative_words: # negative word pass
        negative_word_count+=1 # negative word counter

      if i in positive_words: # positive word pass
        positive_word_count+=1 # positive word counter

      complex_word,syllable_count,syllable_word_count=syllable_and_count(i,syllable_count,syllable_word_count,complex_word) #calling syllable_and_count function
    if all_words==0:
      print("*********** All Words are zero ************")

      #setting all valuse to NAN if link responce is NAN
      POSITIVE_SCORE.append("0")
      NEGATIVE_SCORE.append("0")
      POLARITY_SCORE.append("0")
      SUBJECTIVITY_SCORE.append("0")
      AVG_SENTENCE_LENGTH.append("0")
      PercentageOfComplexWords.append("0")
      FogIndex.append("0")
      AVG_NUMBER_OF_WORDS_PER_SENTENCE.append("0")
      COMPLEX_WORD_COUNT.append("0")
      WORD_COUNT.append("0")
      SYLLABLE_PER_WORD.append("0")
      PERSONAL_PRONOUNS.append("0")
      AVG_WORD_LENGTH.append("0")
      continue


    polarity_score = (positive_word_count - negative_word_count) / ((positive_word_count + negative_word_count) + 0.000001) # calculating plock
    subjectivity_score = (positive_word_count - negative_word_count) / (all_words + 0.000001) # calculating subjectivity_score

    Average_Sentence_Length = all_words / number_of_sentences
    Percentage_of_Complex_words = complex_word / all_words
    Fog_Index = 0.4 * (Average_Sentence_Length + Percentage_of_Complex_words)


    #appending calculation to the specific list Respectively 
    POSITIVE_SCORE.append(positive_word_count)
    NEGATIVE_SCORE.append(negative_word_count)
    POLARITY_SCORE.append(polarity_score)
    SUBJECTIVITY_SCORE.append(subjectivity_score)
    AVG_SENTENCE_LENGTH.append(Average_Sentence_Length)
    PercentageOfComplexWords.append(Percentage_of_Complex_words)
    FogIndex.append(Fog_Index)
    AVG_NUMBER_OF_WORDS_PER_SENTENCE.append(len(doc)/Average_Sentence_Length)
    COMPLEX_WORD_COUNT.append(complex_word)
    WORD_COUNT.append(all_words)
    SYLLABLE_PER_WORD.append(syllable_count/syllable_word_count)
    PERSONAL_PRONOUNS.append(len(pronouns))
    AVG_WORD_LENGTH.append(len(doc)/all_words)
  
  else:
    print("*********** NaN found ************")

    #setting all valuse to NAN if link responce is NAN
    POSITIVE_SCORE.append("nan")
    NEGATIVE_SCORE.append("nan")
    POLARITY_SCORE.append("nan")
    SUBJECTIVITY_SCORE.append("nan")
    AVG_SENTENCE_LENGTH.append("nan")
    PercentageOfComplexWords.append("nan")
    FogIndex.append("nan")
    AVG_NUMBER_OF_WORDS_PER_SENTENCE.append("nan")
    COMPLEX_WORD_COUNT.append("nan")
    WORD_COUNT.append("nan")
    SYLLABLE_PER_WORD.append("nan")
    PERSONAL_PRONOUNS.append("nan")
    AVG_WORD_LENGTH.append("nan")


  print(f"completed URL == {url_no}")

import pandas as pd

# creating cata frame 
df = pd.DataFrame(columns = ['URL_ID' ,'URL' ,  'POSITIVE SCORE' , 'NEGATIVE SCORE' ,'POLARITY SCORE' ,'SUBJECTIVITY SCORE','AVG SENTENCE LENGTH','PERCENTAGE OF COMPLEX WORDS','FOG INDEX','AVG NUMBER OF WORDS PER SENTENCE','COMPLEX WORD COUNT','WORD COUNT','SYLLABLE PER WORD','PERSONAL PRONOUNS','AVG WORD LENGTH'])

# Adding values to dataframe 
for i in range (0,len(POSITIVE_SCORE)):
# for i in range (394,490):

  list_1 = [
            URL_ID[i],
            URL[i],
            POSITIVE_SCORE[i],
            NEGATIVE_SCORE[i],
            POLARITY_SCORE[i],
            SUBJECTIVITY_SCORE[i],
            AVG_SENTENCE_LENGTH[i],
            PercentageOfComplexWords[i],
            FogIndex[i],
            AVG_NUMBER_OF_WORDS_PER_SENTENCE[i],
            COMPLEX_WORD_COUNT[i],
            WORD_COUNT[i],
            PERSONAL_PRONOUNS[i],
            SYLLABLE_PER_WORD[i],
            AVG_WORD_LENGTH[i]
            ]
  df.loc[len(df)] = list_1

#setting file name 
file_name = 'OutPut_1.xlsx'
  
# saving the excel
df.to_excel(file_name,index=False) 
# display
print(df)

