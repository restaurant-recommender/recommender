from flask import Flask, request, jsonify
from flask_cors import CORS

from recommender import NearByRecommender, SimpleRecommender
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

if __name__ == '__main__':
    print(env.PORT)
    app.run(port=env.PORT)
