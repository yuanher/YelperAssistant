"""
@author: Lim Yuan Her
"""

import numpy as np
import pandas as pd
from math import sqrt
import os
import sys
from core.Algorithm.AlgoBase import AlgoBase
from surprise import Reader, Dataset
from surprise import SVDpp

class SurpriseSVDppRecommender(AlgoBase):

    def __init__(self, dsReader):
        AlgoBase.__init__(self, dsReader)
        self.RECOMMENDER_NAME = "SVD++ Recommender"
        self.ratings_ts = dsReader.getRatingsTS()
        self.dsReader = dsReader
        
        foldername, filename = "Models", "SVDppModel_Surprise.pkl"

        if(AlgoBase.checkPathExists(self, foldername, filename) == True):
            self.model = AlgoBase.loadModel(self, foldername, filename)
        else:
            self.fit()

    def fit(self):
        self.model = SVDpp(n_epochs=40, lr_all=0.01, reg_all=0.2)
        self.model.fit(self.train)
        AlgoBase.saveModel(self, self.model, "Models", "SVDppModel_Surprise.pkl")

    def recommend(self, user_id, K=5):

        try:
            trainset = self.ratings_ts.build_full_trainset()
            fill = trainset.global_mean
            anti_testset = []
            u = trainset.to_inner_uid(user_id)
            user_items = set([j for (j, _) in trainset.ur[u]])

            anti_testset += [(trainset.to_raw_uid(u), trainset.to_raw_iid(i), fill) for
                                            i in trainset.all_items() if
                                            i not in user_items]
            testSet = anti_testset
                    
            predictions = self.model.test(testSet)

            recommendations = []

            for user_id, business_id, _, estimatedRating, _ in predictions:
                recommendations.append((business_id, estimatedRating))

            recommendations.sort(key=lambda x: x[1], reverse=True)

            #print(recommendations)
            recList = []

            for ratings in recommendations[:K]:
                (bizId, name, full_addr, categories) = self.dsReader.getBusiness(ratings[0])
                recList.append({
                                "businessID": bizId,
                                "Name": name,
                                "Address": full_addr,
                                "Categories": categories,
                                "EstRating": round(ratings[1], 2)
                            }
                )
        except Exception as error:
            recList = []
            return recList

        return recList