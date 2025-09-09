#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientists = [{"id": scientist.id, "name": scientist.name, "field_of_study": scientist.field_of_study} \
                   for scientist in Scientist.query.all()]
        return make_response(scientists, 200)
    
    def post(self):
        data = request.get_json() 
        try:
            new_scientist = Scientist(name=data.get('name'), field_of_study=data.get('field_of_study'))
            db.session.add(new_scientist)
            db.session.commit()
            return make_response(new_scientist.to_dict(), 201)
        except ValueError:
            db.session.rollback()
            return {'errors': ["validation errors"]}, 400
    
class ScientistByID(Resource):
    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if scientist:
            return make_response(scientist.to_dict(), 200)   
        return {'error': 'Scientist not found'}, 404

    def patch(self, id):
        data = request.get_json()
        scientist = Scientist.query.filter(Scientist.id == id).first()

        if scientist:
            try:
                for attr in data:
                    setattr(scientist, attr, data[attr])
                db.session.add(scientist)
                db.session.commit()
                return make_response(scientist.to_dict(), 202)
            except ValueError:
                db.session.rollback()
                return {'errors': ["validation errors"]}, 400

        return {'error': 'Scientist not found'}, 404
    
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            return '', 204
        return {'error': 'Scientist not found'}, 404

class Planets(Resource):
    def get(self):
        planets = [{"id": planet.id, "name": planet.name, "distance_from_earth": planet.distance_from_earth, \
                   "nearest_star": planet.nearest_star } for planet in Planet.query.all()]
        return make_response(planets, 200)

    
class Missions(Resource):
    def post(self):
        data = request.get_json()
        scientist = Scientist.query.filter(Scientist.id == data.get('scientist_id')).first()
        planet = Planet.query.filter(Planet.id == data.get('planet_id')).first()

        if scientist and planet:
            try:
                new_mission = Mission(name=data.get('name'), \
                                scientist_id=data.get('scientist_id'), \
                                planet_id=data.get('planet_id'))
                db.session.add(new_mission)
                db.session.commit()
                return make_response(new_mission.to_dict(), 201)
            except ValueError:
                db.session.rollback()
                return {'errors': ["validation errors"]}, 400
            
        return {'errors': ["validation errors"]}, 400

api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistByID, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
