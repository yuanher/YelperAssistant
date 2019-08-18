"""
@author: Lim Yuan Her
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.feature_extraction.text import TfidfVectorizer
import os
from core.Algorithm.AlgoBase import AlgoBase

class TfidfRecommender(AlgoBase):

    def __init__(self, dsReader):
        AlgoBase.__init__(self, dsReader)
        self.RECOMMENDER_NAME = "TF=IDF Recommender"

        foldername, filename = "Models", "TfidfModel.pkl"

        if(AlgoBase.checkPathExists(self, foldername, filename) == True):
            self.similarityM = AlgoBase.loadModel(self, foldername, filename)
        else:
            self.fit()

        self.business_data = self.dsReader.getBusinessesData()

    def fit(self, similarity="cosine"):     
        try:
            ratings_data = self.dsReader.getRatingsData()

            # Replace null category value to empty string for post-processing
            self.business_data.fillna({'categories':''}, inplace=True)

            business_filtered = self.business_data[self.business_data.business_id.isin(ratings_data.business_id)]
            
            corpus = business_filtered["categories"]
            self.business_ids = business_filtered['business_id'].tolist()

            vectorizer = TfidfVectorizer()
            X = vectorizer.fit_transform(corpus)
            self.X_df = pd.DataFrame(X.todense(), columns = vectorizer.get_feature_names(), index=self.business_ids)

            self.X_df = self.X_df.mask(self.X_df > 0, 1)
            self.X_df = self.X_df.astype(int)

            self.Similarity_Matrix = self.Compute_Similarity(similarity)
            AlgoBase.saveModel(self, self.Similarity_Matrix, "Models", "TfidfModel.pkl")
        except Exception as e:
            print(e)

    def Compute_Similarity(self, similarity):
        self.similarity = similarity
        title_labels = self.business_ids
        #id_labels = [self.BooksM[self.BooksM['Book-Title'] == label]['ISBN'].values[0] for label in title_labels]

        if(similarity == "corr"):
            #self.similarityM = self.X_df.corr().round(4)
            sim_array = np.corrcoef(self.X_df.values)
            self.similarityM = pd.DataFrame(data=sim_array, index=title_labels, columns=title_labels)
        elif(similarity == "cosine"):
            sim_array = cosine_similarity(self.X_df)
            self.similarityM = pd.DataFrame(data=sim_array, index=title_labels, columns=title_labels)
        elif(similarity == "adj_cosine"):
            M = np.asarray(self.X_df)
            M_mean = M.mean(axis=1)
            M_mean_adj = M - M_mean[:, None]
            sim_array = cosine_similarity(M_mean_adj)
            self.similarityM = pd.DataFrame(data=sim_array, index=title_labels, columns=title_labels)
        elif(similarity == "euclidean"):
            sim_array = euclidean_distances(self.X_df)
            self.similarityM = pd.DataFrame(data=sim_array, index=title_labels, columns=title_labels)

        return self.similarityM

    def recommend(self, user_id, K = 5):
        try:
            # Generates list of businesses rated by user
            df_user_business_list = self.dsReader.getUserBusinessList(user_id)
            df_user_business_list = df_user_business_list.sort_values(by='stars', ascending=False)
            df_user_business_list = df_user_business_list[["business_id"]]

            # Combine similarity ratings for high-rated businesses
            df_similarityM = self.similarityM.reset_index().rename(columns={self.similarityM.index.name:'business_id'})
            df_user_business_list_sim = df_user_business_list.merge(df_similarityM, how = 'left', left_on = 'business_id', right_on = 'index')

            # Get top 6 businesses with highest cosine similarity for each user-rated business
            df = np.argsort(df_user_business_list_sim.iloc[:, 2:],axis=1).iloc[:,-6:]

            # Add to list for sorting
            business_ids_sim = []
            for i in range(len(df)): 
                for j in range(5):
                    business_id_sim = df_user_business_list_sim.iloc[:, 2:].columns[df.iloc[i,j]]
                    business_ids_sim.append(business_id_sim)

            # Get count of each business in list and sort in descending order by count
            simlist_Count = { x:business_ids_sim.count(x) for x in business_ids_sim }
            simlist_Count = sorted(simlist_Count.items(), key=lambda x: x[1], reverse=True)

            # Compile recommended list
            recList = []
            for idx, (id, _) in enumerate(simlist_Count):
                # Get average rating for business
                rating = self.business_data[self.business_data.business_id == id]['stars'].values[0]
                # Get business information
                (bizId, name, full_addr, categories) = self.dsReader.getBusiness(id)
                recList.append({
                                "businessID": bizId,
                                "Name": name,
                                "Address": full_addr,
                                "Categories": categories,
                                "EstRating": round(rating, 2)
                            }
                )    
                if idx == K - 1:       
                    break  

        except Exception:
            recList = []
            return recList

        return recList