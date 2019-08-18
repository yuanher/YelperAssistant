from flask import Blueprint
from flask_restplus import Api
from apis.recommend import ns as recommend
from apis.user import ns as user
from apis.rating import ns as rating

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(blueprint,
    title='Yelper Assistant Recommender',
    version='1.0',
    description='Provides recommendations from Yelp',
    # All API metadatas
)

api.add_namespace(recommend)
api.add_namespace(user)
api.add_namespace(rating)