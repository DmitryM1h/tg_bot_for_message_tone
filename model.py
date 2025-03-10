import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import pickle
'''from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords'''
import numpy as np

def preprocess(text:str) -> str :
    #text = re.sub(r"http:\S*","",text)
    text = re.sub(r'http[s]?://\S+|www\.\S+', '', text)
    text = re.sub(r"[\n\r.,]"," ",text)
    #text = re.sub(r"[():!;\"|]*","",text)
    text = re.sub(r"[#@][\S]*","",text)
    text = re.sub(r"RT","",text)
    #emoticons = re.findall(r"[XХ:][3ЗD()]+", text)
    #print(emoticons)
    #text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r" {1,}", " ",text).strip()
    return str.lower(text)
    
'''def preprocess(text: str) -> str:
    if not isinstance(text,str):
        raise ValueError("preprocess принимает string!")
    text = re.sub(r'http[s]?://\S+|www\.\S+', '', text)
    text = re.sub(r"[\n\r.,]", " ", text)
    text = re.sub(r"[():!;\"|]*", "", text)
    text = re.sub(r"[#@]\S*", "", text)
    text = re.sub(r"RT", "", text)
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r" +", " ", text).strip()
    return str.lower(text)'''

'''def tokenizer_porter(text: str)->str:
    if not isinstance(text,str):
        raise ValueError("tokenizer_porter принимает string!")
    words = [porter.stem(word) for word in text.split()]
    nostop = [word for word in words if word not in stop]
    return " ".join(nostop)'''

class Model:
    def __init__(self):
        with open('model.pkl', 'rb') as file:
            self.__loaded_model = pickle.load(file)
        with open('tfidf_vectorizer.pkl', 'rb') as file:
            self.__tfidf = pickle.load(file)


    def prepare(self,text):
        a = list(map(preprocess,text))
        sparse_matrix = self.__tfidf.transform(a)
        return sparse_matrix

    def predict(self,text):
        clf = self.__loaded_model
        prepared_text = self.prepare(text)
        prediction = clf.predict(prepared_text)
        return prediction

    def predict_proba(self,text):
        clf = self.__loaded_model
        prepared_text = self.prepare(text)
        prediction = clf.predict_proba(prepared_text)[0]
        return np.round(prediction,5)
