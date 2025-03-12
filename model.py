import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import pickle
import numpy as np
#import abstract_model as abm
from abstract_model import Imodel
class Log_reg_tone(Imodel):
    def __init__(self):
        with open('loaded_models/model.pkl', 'rb') as file:
            self.loaded_model = pickle.load(file)
        with open('loaded_models/tfidf_vectorizer.pkl', 'rb') as file:
            self.tfidf = pickle.load(file)


    def prepare(self,text):
        a = list(map(self.preprocess,text))
        sparse_matrix = self.tfidf.transform(a)
        return sparse_matrix

    def predict(self,text):
        clf = self.loaded_model
        prepared_text = self.prepare(text)
        prediction = clf.predict(prepared_text)
        return prediction

    def predict_proba(self,text):
        clf = self.loaded_model
        prepared_text = self.prepare(text)
        prediction = clf.predict_proba(prepared_text)[0][1]
        if prediction > 0.5:
            return f"Позитивное с вероятностью {np.round(prediction,5)}"
        else:
            return f"Негативное с вероятностью {1-np.round(prediction,5)}"
    
    def preprocess(self,text:str)->str:
        if not isinstance(text,str):
            raise ValueError("text must be string")
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

