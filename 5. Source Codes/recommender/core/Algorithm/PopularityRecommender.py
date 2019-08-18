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

class PopularityRecommender(AlgoBase):

    def __init__(self, dsReader):
        AlgoBase.__init__(self, dsReader)
        self.RECOMMENDER_NAME = "Popularity Recommender"
        self.dsReader = dsReader
        
        foldername, filename = "Models", "PopularityModel.pkl"

        if(AlgoBase.checkPathExists(self, foldername, filename) == True):
            self.model = AlgoBase.loadModel(self, foldername, filename)
        else:
            self.fit()

    def fit(self):
        # Get business raw data
        business_data = self.dsReader.getBusinessesData()
        # Get ratings raw data
        ratings_data = self.dsReader.getRatingsData()

        # Combine ratings raw data with business raw data
        business_data = pd.merge(ratings_data, business_data, on='business_id')[['user_id', 'business_id', 'name', 'stars_x', 'categories']]
        print(business_data)
        # Get average ratings for each business
        business_data_avgRatings = pd.DataFrame(business_data.groupby('name')['stars_x'].mean())
        print(business_data_avgRatings)
        # Get number of ratings for each business
        business_data_avgRatings['rating_counts'] = pd.DataFrame(business_data.groupby('name')['stars_x'].count())
        print(business_data_avgRatings)
        # Combine average rating/count data with business raw data
        business_data_avgRatings.reset_index(inplace=True)
        business_data_avgRatings = pd.merge(business_data_avgRatings, business_data, on='name')
        print(business_data_avgRatings.columns)
        business_data_avgRatings = business_data_avgRatings[['business_id', 'name', 'stars_x_x', 'rating_counts']]
        print(business_data_avgRatings)
        # Sort data byy number of ratings and stars
        self.model = business_data_avgRatings.sort_values(['rating_counts', 'stars_x_x'], ascending=[False, False])

        # Persist data as recommender model
        AlgoBase.saveModel(self, self.model, "Models", "PopularityModel.pkl")

    def recommend(self, user_id, K=5):

        try:
            recList = []
            
            for index, row in self.model.head(K).iterrows():
                (bizId, name, full_addr, categories) = self.dsReader.getBusiness(row['business_id'])
                recList.append({
                                "businessID": bizId,
                                "Name": name,
                                "Address": full_addr,
                                "Categories": categories,
                                "EstRating": round(row['stars_x_x'], 2)
                            }
                )
        except Exception as error:
            return error

        return recList