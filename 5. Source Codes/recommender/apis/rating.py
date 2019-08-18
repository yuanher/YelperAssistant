from flask_restplus import Namespace, Resource, fields

ns = Namespace('rating', description='Rating operations')

rating = ns.model('rating', {
    'user_id': fields.Integer(required=True, description='User ID'),
    'business_id': fields.Integer(required=True, description='Business ID'),
    'rating': fields.Float(required=True, description='Given Rating')
})

@ns.route('/<int:user_id>')
@ns.response(404, 'user not found')
@ns.param('user_id', 'User ID')
class Rating(Resource):
    '''Show all rating information'''
    @ns.doc('get_rating')
    @ns.marshal_with(rating)
    def get(self, user_id):
        '''Get rating details'''
        rating = {
            "user_id": 123,
            "business_id": 345,
            "rating": 4.0
        }
        return rating

@ns.route('/')		
class RatingList(Resource):
    @ns.doc('create_rating')
    @ns.expect(rating)
    @ns.marshal_with(rating, code=201)
    def post(self):
        '''Create a new rating'''
        rating = {
            "user_id": 123,
            "business_id": 345,
            "rating": 4.0
        }
        return rating