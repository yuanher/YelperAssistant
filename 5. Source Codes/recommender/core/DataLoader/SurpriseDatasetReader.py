import os

import numpy as np
import pandas as pd
from surprise import Reader, Dataset
from surprise.model_selection import train_test_split
import pickle
import itertools
import collections

class SurpriseDatasetReader:

    ratingsPath = 'core/DataLoader/DataSet/review_enc_20K.csv'
    businessesPath = 'core/DataLoader/DataSet/business_enc.csv'
    usersPath = 'core/DataLoader/DataSet/user_enc.csv'
    usersMappingPath = 'core/DataLoader/DataSet/user_mapping.pickle'
    businessesMappingPath = 'core/DataLoader/DataSet/business_mapping.pickle'

    def __init__(self):

        self.ratings = None
        self.businesses = None
        self.users = None
        self.ratings_matrix = None

    def loadData(self):

        # Load books data into memory
        df_businesses = pd.read_csv(self.businessesPath, delimiter=",", error_bad_lines=False, encoding='latin-1', header=0, index_col=False, low_memory=False)
        
        # Load users data into memory
        df_users = pd.read_csv(self.usersPath, delimiter=",", error_bad_lines=False, encoding='latin-1', header=0, index_col=False, low_memory=False)

        # Load ratings data into memory
        df_ratings = pd.read_csv(self.ratingsPath, delimiter=",", header=0, encoding ='unicode_escape', index_col=False, low_memory=False)
        df_ratings_nodup = df_ratings.drop_duplicates(subset =["user_id", "business_id"], keep = False)
        #df_ratings_nodup.set_index(['user_id', 'business_id'], append=True, inplace=True)

        self.userMapping = self.loadMappings(self.usersMappingPath)
        self.businessMapping = self.loadMappings(self.businessesMappingPath)

        #print(list(itertools.islice(self.businessMapping.items(), 0, 4)))

        ratings_dict = {'itemID': list(df_ratings_nodup.business_id),
                        'userID': list(df_ratings_nodup.user_id),
                        'rating': list(df_ratings_nodup.stars)}
        df_ratingsS = pd.DataFrame(ratings_dict)

        reader = Reader(rating_scale=(0.5, 5.0))
        self.ratings_ts = Dataset.load_from_df(df_ratingsS[['userID', 'itemID', 'rating']], reader)

        self.ratings = df_ratings_nodup
        self.businesses = df_businesses
        self.users = df_users

        return (self.businesses, self.users, self.ratings)

    def getBusinessDetails(self, businessId):
        businessName = self.businesses[self.businesses["business_id"] == businessId]["name"].values[0]
        businessAddress = self.businesses[self.businesses["business_id"] == businessId]["address"].values[0]
        businessNumReviews = self.businesses[self.businesses["business_id"] == businessId]["review_count"].values[0]
        return  (businessName, businessAddress, businessNumReviews)

    def getRatingsMatrix(self):
        return self.ratings_matrix

    def getBusinessesData(self):
        return self.businesses

    def getUsersData(self):
        return self.users

    def getRatingsData(self):
        return self.ratings

    def getRatingsTS(self):
        return self.ratings_ts

    def getBusinessById(self, businessId):
        return self.businesses[self.businesses["business_id"] == businessId]

    def getBusinessesByIds(self, business_ids):
        return self.businesses[self.businesses["business_id"].isin(business_ids)]

    def getAvgRatingById(self, business_id):
        d = {'stars': ['mean']}
        res = self.ratings[self.ratings["business_id"] == business_id].groupby('business_id').agg(d)
        res.columns = res.columns.droplevel(0)
        res = res.rename({'mean': 'stars'}, axis=1)
        res = res.reset_index()

        return res

    def getUserNumRatings(self, user_id):
        res = len(self.ratings[self.ratings["user_id"] == user_id])
        return res

    def getUserRatedBusinessNames(self, userId):
        userRatedBusinessIds = self.ratings[self.ratings["user_id"] == userId].business_id.unique().tolist()
        return self.getBusinessesByIds(userRatedBusinessIds)[["business_id", "name"]]

    def getUserBusinessList(self, userId):
        # Get the user's data and merge in the book information.
        user_ratedbusinesses_df = self.ratings[self.ratings["user_id"] == userId]

        user_businesses_list = user_ratedbusinesses_df.merge(self.businesses, how = 'left', left_on = 'business_id', right_on = 'business_id').rename(columns={'stars_x': 'stars'}).sort_values(['stars'], ascending=False)
        
        return user_businesses_list

    def getUserDetails(self, userId):
        name = self.users[self.users['user_id'] == userId][['name']].values[0][0]
        avgrating = self.users[self.users['user_id'] == userId][['average_stars']].values[0][0]
        numratings = self.users[self.users['user_id'] == userId][['review_count']].values[0][0]

        return name, avgrating, numratings

    def getBusinessIdByTitle(self, name):
        return self.businesses[self.businesses['name'] == name]['business_id'].values[0]

    def getBusiness(self, id):
        name = self.businesses[self.businesses["business_id"] == id][['name']].values[0][0]
        full_addr = self.businesses[self.businesses["business_id"] == id][['address', 'city', 'state', 'postal_code']]
        full_addr_list = full_addr.melt().value.tolist()
        full_addr_str = ""
        for item in full_addr_list:
            full_addr_str = full_addr_str + str(item)
        categories = self.businesses[self.businesses["business_id"] == id][['categories']].values[0][0]

        idx = list(self.businessMapping.values()).index(id)
        bizId = list(self.businessMapping.keys())[idx]
        return (bizId, name, full_addr_str, categories)

    def save_data(self, ds, ds_type):
        if ds_type == "user":
            ds.to_csv(self.usersPath, index=False)
        elif ds_type == "business":
            ds.to_csv(self.businessesPath, index=False)    
        elif ds_type == "rating":   
            ds.to_csv(self.ratingsPath, index=False)  

    def addUser(self, name, review_count, yelping_since, useful, fans, average_stars):
        userId = self.users['user_id'].max() + 1
        self.users = self.users.append({'user_id':str(userId), 'name':name, 'review_count':review_count,                                     'yelping_since':yelping_since, 'useful':useful, 
                                        'fans':fans, 'average_stars':average_stars}, ignore_index=True)
        self.save_data(self.users, "user")
        
        return userId

    def addBusiness(self, address,categories,city,hours,latitude,longitude,name,postal_code,state,business_id):
        self.businesses = self.businesses.append({'business_id':business_id, 
                                                  'address':address, 
                                                  'categories':categories,
                                                  'state':state, 
                                                  'city':city, 
                                                  'postal_code':postal_code,
                                                  'hours':hours, 
                                                  'latitude':latitude, 
                                                  'longitude':longitude, 
                                                  'name':name}, ignore_index=True)
        self.save_data(self.businesses, "business")
    
    def addRating(self, userId, id, rating):
        self.ratings = self.ratings.append({'user_id':userId, 'business_id':id, 'stars':rating},                                                     ignore_index=True)
        self.save_data(self.ratings, "rating") 

    def train_test_split(self):
        train, test = train_test_split(self.ratings_ts, test_size=.2)

        return train, test

    def loadMappings(self, filename):

        infile = open(filename,'rb')
        mapping = pickle.load(infile)
        infile.close()

        return mapping