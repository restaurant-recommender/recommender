from flask import Flask, request, jsonify
from flask_cors import CORS

from recommender import NearByRecommender, simple_recommender
from recommender.genetic_algorithm_recommender import genetic_algorithm_recommender
import env

app = Flask(__name__)
CORS(app)

try:
    import googleclouddebugger
    googleclouddebugger.enable(
        breakpoint_enable_canary=True
    )
except ImportError:
    pass

@app.route("/")
def helloWorld():
    return "Hello, cross-origin-world!"

@app.route("/_hc")
def health_check():
    return "ok"

@app.route("/recommend/nearby", methods=['POST'])
def nearby_recommend():
    data = request.json
    recommender = NearByRecommender(batch_size=10)
    restaurant_ids = recommender.recommend(data)
    print(restaurant_ids)
    return jsonify({
        'status': True,
        'restaurant_ids': restaurant_ids
    })

@app.route("/recommend/simple", methods=['POST'])
def simple_recommend():
    data = request.json
    recommender = SimpleRecommender()
    restaurant_ids = recommender.recommend(data)
    print(restaurant_ids)
    return jsonify({
        'status': True,
        'restaurant_ids': restaurant_ids
    })

# Restaurant: {
#     _id: string
#     profile: {
#         categories: {
#             name_en: string
#         }[]
#         price_range: number
#     }
# }
# User: {
#     categories: string[]
#     price_range: number
# }
# History: {
#     user: string
#     histories: {
#         restaurant: string
#         love: number
#         hate: number
#     }[]
# }

@app.route("/recommend/genetic", methods=['POST'])
def genetic_recommend():
    default_count = 6
    try:
        data = request.json
        count = int(request.args.get('count')) or default_count
        print(f'Got new genetic request, count: {count}')
        restaurants = genetic_algorithm_recommender(data['restaurants'], data['users'], genes=count)
        print(f"Generated {len(restaurants)}")
        return jsonify({
            'status': True,
            'restaurants': restaurants,
        })
    except Exception as error:
        print(error)
        return jsonify({
            'status': False,
            'message': str(error),
        })

if __name__ == '__main__':
    print(env.PORT)
    app.run(port=env.PORT)
