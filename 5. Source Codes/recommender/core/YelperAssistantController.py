from core.Algorithm.SurpriseSVDppRecommender import SurpriseSVDppRecommender
from core.Algorithm.PopularityRecommender import PopularityRecommender
from core.Algorithm.TfidfRecommender import TfidfRecommender
from core.Algorithm.AlgoBase import AlgoBase

from core.DataLoader.SurpriseDatasetReader import SurpriseDatasetReader

class YelperAssistantController(object):

    def __init__(self):
        self.dsReader = SurpriseDatasetReader()  
        self.dsReader.loadData()
        #print("Data Load Complete")

    def addUser(self, name, review_count, yelping_since, useful, fans, average_stars):
         self.userId = self.dsReader.addUser(name, review_count, yelping_since, useful, fans, average_stars)
         return self.userId

    def getUser(self, userId):
         name, avgrating, numratings = self.dsReader.getUserDetails(userId)
         return (name, avgrating, numratings)
        
    def getRecommender(self, userId):
        try:
            ratings_data = self.dsReader.getRatingsData()
            foundUser = ratings_data[ratings_data['user_id'] == userId].index.tolist()

            # User has given some business ratings
            if(len(foundUser) != 0):
                NumUserRatings = self.dsReader.getUserNumRatings(userId)
                # Use Tfidf Recommender if number of user given ratings is less than 5
                if(NumUserRatings < 5):
                    print("Using Tfidf Recommender...")
                    rec = TfidfRecommender(self.dsReader) 
                # Use SVD++ Recommender if number of user given ratings is more than 5
                else:                        
                    print("Using SVD++ Recommender...")
                    rec = SurpriseSVDppRecommender(self.dsReader) 
            # User has not given any business ratings
            elif(len(foundUser) == 0):
                print("Using Popularity Recommender...")
                rec = PopularityRecommender(self.dsReader) 
            return rec
        except Exception as e:
            print(e)

    def update_models(self):
        try:
            PopularityRecommender(self.dsReader).fit()
            TfidfRecommender(self.dsReader).fit()
            SurpriseSVDppRecommender(self.dsReader).fit()
        except Exception as e:
            print(e)
            result = {
                        "success": False
            }
            return result

        result = {
                    "success": True
        }
        return result