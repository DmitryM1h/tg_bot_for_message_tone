import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import pickle
'''from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords'''
import numpy as np
import scipy
import abstract_model as abm




class Log_reg_agression(abm.Imodel):
    def __init__(self):
        with open('loaded_models/rude_detector.pkl', 'rb') as file:
            self.__loaded_model = pickle.load(file)
        with open('loaded_models/tfidf_rude.pkl', 'rb') as file:
            self.__tfidf = pickle.load(file)


    def prepare(self,text):
        text = pd.DataFrame({"ttext":text})
        text['text_clear'] = text['ttext'].apply(self.preprocess)
        
        sparse_matrix = self.__tfidf.transform(text['text_clear'])
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
        return f"Позитивное с вероятностью {np.round(prediction,5)}"

    
    def preprocess(text:str) -> str :
        #text = re.sub(r"http:\S*","",text)
        emoticons = re.findall(r"[XХ:=][3зЗD()]+", text)
        emoticons += re.findall(r"[0оОoO]_[0оОoO]", text)
        text = re.sub(r'http[s]?://\S+|www\.\S+', '', text)
        text = re.sub(r"@\S+[: ]","",text)
        text = re.sub(r"[XХ:][3ЗD()]+"," ", text)
        text = re.sub(r"[\n\r.,]"," ",text)
        text = re.sub(r"\W"," ",text)
        text = re.sub(r"[():!;?\"|]*","",text)
        text = re.sub(r"[#@][\S]*","",text)
        text = re.sub(r"RT","",text)
        text = re.sub(r'\d+', '', text)
        text = re.sub(r" {1,}", " ",text).strip()
        return str.lower(text) +" "+" ".join(emoticons)
