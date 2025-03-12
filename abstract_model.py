from abc import ABC, abstractmethod
import re

class Imodel:
    @abstractmethod
    def prepare(self,text):
        pass
    @abstractmethod
    def predict(self,text):
        pass
    @abstractmethod
    def predict_proba(self,text):
        pass
    @abstractmethod
    def preprocess(text:str)->str:
        pass
      



