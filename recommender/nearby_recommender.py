import sys
sys.path.append('..')

from recommender import Recommender
from client.app_server import Client

class NearByRecommender(Recommender):
    def __init__(self, batch_size=10):
        self.batch_size = batch_size

    def recommend(self, data: object) -> list:
        print(data)
        latitude = data['location']['coordinates'][1]
        longitude = data['location']['coordinates'][0]
        recommended_count = len(data['histories'])
        recommendation_limit = self.batch_size
        print(recommended_count)
        print(recommendation_limit)
        nearby_restaurants = Client().restaurant_get_nearby(latitude, longitude, limit=recommendation_limit, skip=recommended_count)
        nearby_restaurant_ids = [nearby_restaurant['_id'] for nearby_restaurant in nearby_restaurants]
        return nearby_restaurant_ids
        # return []
