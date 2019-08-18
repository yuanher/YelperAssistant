import numpy as np
import pandas as pd
import pickle
from math import sqrt
from core.Evaluator.Evaluator import Evaluator
from sklearn.metrics import mean_squared_error
import os
import sys

class AlgoBase():

    def __init__(self, dsReader):
        self.dsReader = dsReader
        self.RECOMMENDER_NAME = ""  
        self.train, self.test = self.dsReader.train_test_split()   
        self.current_dir = os.path.dirname(__file__) 

    def fit(self, similarity="cosine"):  
        pass

    def recommend(self, user_id, K = 5):
        pass
        
    def Evaluate(self, pred, actual, metricList):
        try:
            evaluator_obj = Evaluator()
            evaluator_obj.addMetric(metricList)
            eval_res = evaluator_obj.Evaluate(pred, actual)

            print()
            print("Evaluation Results:")
            for key, value in eval_res.items():
                print("{}: {:.2f}".format(key, value))
            print()

        except Exception as e:
            print(e)

    def saveModel(self, model, folder_path, file_name):

        filepath = os.path.realpath("{0}/{1}/{2}".format(self.current_dir, folder_path, file_name))
        f = open(filepath, "wb")
        pickle.dump(model, f)

    def loadModel(self, folder_path, file_name):

        filepath = os.path.realpath("{0}/{1}/{2}".format(self.current_dir, folder_path, file_name))
        f = open(filepath, "rb")
        model = pickle.load(f)

        return model

    def checkPathExists(self, folder_path, file_name):

        filepath = os.path.realpath("{0}/{1}/{2}".format(self.current_dir, folder_path, file_name))       

        if(os.path.exists(filepath)):
            return True
        else:
            return False