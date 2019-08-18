from flask_restplus import Namespace, Resource, fields
from core.YelperAssistantController import YelperAssistantController

yelpController = YelperAssistantController()
ns = Namespace('user', description='User operations')

userDetails = ns.model('userDetails', {
    'user_id': fields.Integer(required=True, description='User ID'),
    'name': fields.String(required=True, description='Uaer name'),
    'review_count': fields.Integer(required=False, description='Number of reviews'),
    #'yelping_since': fields.String(required=False, description='Date joined'),
    #'useful': fields.Integer(required=False, description='Number of useful reviews'),
    #'fans': fields.Integer(required=False, description='Number of fans'),
    'average_stars': fields.Float(required=False, description='Average rating')
})

userNew = ns.model('userNew', {
    'name': fields.String(required=True, description='Uaer name')
})

userNewResp = ns.model('userNewResp', {
    'user_id': fields.Integer(required=True, description='Uaer ID')
})


@ns.route('/<int:user_id>')
@ns.response(404, 'user not found')
@ns.param('user_id', 'User ID')
class User(Resource):
    '''Show all recommendations'''
    @ns.doc('get_user')
    @ns.marshal_with(userDetails)
    def get(self, user_id):
        '''Get user details'''
        name, avgrating, numratings = yelpController.getUser(user_id)

        res = {
		    "user_id": user_id,
            'name': name,
            'review_count': numratings,
            'average_stars': avgrating
        }
        
        return res

@ns.route('/')		
class UserList(Resource):
    @ns.doc('create_user')
    @ns.expect(userNew)
    @ns.marshal_with(userNewResp, code=201)
    def post(self):
        '''Create a new user'''
        #reqParams = api.payload
        #print("New user name:", reqParams["name"])
        userId = yelpController.addUser("test")

        res = {
            "user_id": userId
        }

        return res