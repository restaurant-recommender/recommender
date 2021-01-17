import sys
sys.path.append('..')

import requests
import env

class Client:

    @staticmethod
    def restaurant_get_nearby(latitude, longitude, distance=None, limit=None, skip=None, body=None):
        return requests.get(f'{env.APP_SERVER_URL}/api/restaurants/nearby?lat={latitude}&lon={longitude}{f"&dist={distance}" if distance else ""}{f"&limit={limit}" if limit else ""}{f"&skip={skip}" if skip else ""}', json=body).json()

    @staticmethod
    def user_update_profile_weight(user_id, body):
        print(body)
        print('LLLLLOOOOOLLLLLL')
        result = requests.put(f'{env.APP_SERVER_URL}/api/users/{user_id}/profile_weight', json=body)
        print('AAAAAAAAA')
        print(result)

        return result.status_code