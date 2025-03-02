import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import pickle
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import numpy as np

def preprocess(text: str) -> str:
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
    return str.lower(text)

def tokenizer_porter(text):
    if not isinstance(text,str):
        raise ValueError("tokenizer_porter принимает string!")
    words = [porter.stem(word) for word in text.split()]
    nostop = [word for word in words if word not in stop]
    return " ".join(nostop)

class Model:
    def __init__(self):
        with open('model.pkl', 'rb') as file:
            self.__loaded_model = pickle.load(file)
        self.__tfidf = TfidfVectorizer()
        df = pd.read_csv("mydata.csv")
        df['ttext'] = df['ttext'].apply(preprocess)
        #df['ttext'] = df['ttext'].apply(tokenizer_porter)
        self.__tfidf.fit(df['ttext'])

    def prepare(self,word):
        m = pd.DataFrame({'ttext':word})
        m['ttext'] = m['ttext'].apply(preprocess)
        #m['ttext'] = m['ttext'].apply(tokenizer_porter)
        sparse_matrix = self.__tfidf.transform(m['ttext'])
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
