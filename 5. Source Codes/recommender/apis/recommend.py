from flask_restplus import Namespace, Resource, fields
from core.YelperAssistantController import YelperAssistantController
from core.Algorithm.SurpriseSVDppRecommender import SurpriseSVDppRecommender
from core.Algorithm.PopularityRecommender import PopularityRecommender

yelpController = YelperAssistantController()

ns = Namespace('recommend', description='Recommender operations')

recommend = ns.model('Recommend', {
    'businessID': fields.String(required=True, description='Business ID'),
    'Name': fields.String(required=True, description='Business Name'),
    'Address': fields.String(required=True, description='Business Address'),
    'Categories': fields.String(required=True, description='Business Categories'),
    'EstRating': fields.Float(required=False, description='Esimated Rating')
})

update = ns.model('update', {
    'success': fields.Boolean(required=True, description='Update Status')
})

@ns.route('/userid=<int:user_id>')
@ns.response(404, 'user not found')
@ns.param('user_id', 'User ID')
class Recommend(Resource):
    '''Show all recommendations'''
    @ns.doc('get_recommend')
    @ns.marshal_list_with(recommend)
    def get(self, user_id):
        '''Get recommendations based on user ID'''
        rec = yelpController.getRecommender(user_id)
        recList = rec.recommend(user_id, 5)

        return recList

@ns.route('/updateModels')
@ns.response(500, 'Update failed')
class updateModels(Resource):
    '''Update Recommender Models'''
    @ns.doc('update_models')
    @ns.marshal_with(update)
    def get(self):
        '''Update Recommender Models'''
        result = yelpController.update_models()
        print(result)
        return result