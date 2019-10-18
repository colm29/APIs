from findARestaurant import findARestaurant
from models import Base, Restaurant
from flask import Flask, jsonify, request
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

import sys

import config

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


foursquare_client_id = config.CLIENT_ID

foursquare_client_secret = config.CLIENT_SECRET

google_api_key = config.GOOGLE_API_KEY

engine = create_engine('sqlite:///restaurants.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


@app.route('/restaurants', methods=['GET', 'POST'])
def all_restaurants_handler():
    if request.method == 'POST':
        resto = findARestaurant(
            request.args.get('mealType', ''), request.args.get('location', ''))
        resto_for_db = Restaurant(restaurant_name=resto['name'],
                                  restaurant_image=resto['image'], restaurant_address=resto['address'])
        session.add(resto_for_db)
        session.commit()
        resto = session.query(Restaurant).query(
            restaurant_name=resto['name']).one()
        return jsonify(Restaurant=resto.serialize)
    else:
        restos = session.Query(Restaurant).all()
        return jsonify(Restaurants=[r.serialize for r in restos])


@app.route('/restaurants/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def restaurant_handler(id):
    resto = session.query(Restaurant).query(id=id).one()
    if request.method == 'DELETE':
        session.delete(resto)
        session.commit()
        restos = session.Query(Restaurant).all()
        return jsonify(Restaurants=[r.serialize for r in restos])
    elif request == 'PUT':
        if request.args.get('name', '') != '':
            resto.restaurant_name = request.args['name']
        if request.args.get('address', '') != '':
            resto.restaurant_address = request.args['address']
        if request.args.get('image', '') != '':
            resto.restaurant_address = request.args['image']
        session.add(resto)
        session.commit()
    return jsonify(Restaurant=resto.serialize)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
