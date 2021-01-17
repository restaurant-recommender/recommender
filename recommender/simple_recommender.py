import sys
sys.path.append('..')

from recommender import Recommender
from client.app_server import Client
import random


class SimpleRecommender(Recommender):
    def __init__(self, batch_size=20, love_weight=0.5, hate_weight=-1):
        self.batch_size = batch_size
        self.love_weight = love_weight
        self.hate_weight = hate_weight

    def _get_updated_weight(self, user, recent_histories) -> dict:
        updated_profile_weight = {}
        for category in user['profile']["preference"]["categories"]:
            print(category)
            updated_profile_weight[category['category']] = float(category['value'])
        for history in recent_histories:
            print(history)
            for category in history['restaurant']['profile']['categories']:
                if category['_id'] in updated_profile_weight:
                    updated_profile_weight[category['_id']] += history['rating'] if history['rating'] < 0 else (history['rating'] / 2) 
        return updated_profile_weight



    def recommend(self, data: object) -> list:
        print('-----------------------------------------------------')
        print(data)
        latitude = data['location']['coordinates'][1]
        longitude = data['location']['coordinates'][0]
        recommended_count = len(data['histories'])
        limit = recommended_count + (2 * self.batch_size)
        matched_count = (self.batch_size / 4) - 1
        random_count = 1

        updated_weight = self._get_updated_weight(data['users'][0], data['histories'][:self.batch_size])
        print(updated_weight)
        Client().user_update_profile_weight(data['users'][0]['_id'], [{"category_id": data[0], "value": data[1]} for data in updated_weight.items()])


        recommeded_restaetant_ids = [restaurant['_id'] for restaurant in data['histories']]
        nearby_restaurants = Client().restaurant_get_nearby(latitude, longitude, limit=limit, skip=recommended_count)

        available_restaurants = [restaurant for restaurant in nearby_restaurants if restaurant['_id'] not in recommeded_restaetant_ids]
        print([restaurant['_id'] for restaurant in available_restaurants])
        top_categories = set([category[0] for category in sorted(updated_weight.items(), key=lambda x: x[1], reverse=True)[:3]])

        # print(top_categories)

        # top_categories = set([category['_id'] for category in sorted(data["users"][0]["profile"]["preference"]["categories"], key=lambda x: x["value"], reverse=True)[:3]])
        sorted_restaurants = sorted(available_restaurants, key=lambda restaurant: len(top_categories.intersection(set([category['_id'] for category in restaurant['profile']['categories']]))), reverse=True)
        sorted_restautant_ids = [restaurant['_id'] for restaurant in sorted_restaurants]
 
        new_recommended_ids = []
        for i in range(4):
            matched_ids = sorted_restautant_ids[:4]
            random.shuffle(matched_ids)
            random_ids = [sorted_restautant_ids[random.randint(4, len(sorted_restautant_ids) - 5)]]
            adding_ids = matched_ids + random_ids
            for adding_id in adding_ids:
                sorted_restautant_ids.pop(sorted_restautant_ids.index(adding_id))
            new_recommended_ids += adding_ids

        print(new_recommended_ids)
        return new_recommended_ids
