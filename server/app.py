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



class Home(Resource):
    def get(self):
       return make_response({}, 200)


class Scientists(Resource):
    def get(self):
        scientists = Scientist.query.all()
        scientists_dict = [scientist.to_dict_2() for scientist in scientists]
        return make_response(scientists_dict, 200)

    def post(self):
        json_data = request.get_json()
        if not json_data.get('field_of_study'):
            return {'errors': ['validation errors']}, 400
        new_record = Scientist(
            name=json_data.get('name'),
            field_of_study=json_data.get('field_of_study')
        )
        db.session.add(new_record)
        db.session.commit()
        if not new_record.id:
            return {}, 400
        return make_response(new_record.to_dict(), 201)

class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id==id).first()
        if not scientist:
            return {'error': 'Scientist not found'}, 400
        return make_response(scientist.to_dict(), 200)

    def patch(self, id):
        scientist = Scientist.query.filter(Scientist.id==id).first()
        if not scientist:
            return {'error': 'Scientist not found'}, 404   
        json_data = request.get_json()

        for key, value in json_data.items():
            if hasattr(scientist, key):
                if not value: 
                    return {'errors': ["validation errors"]}, 400
                setattr(scientist, key, value)
            else:
                return {'error': 'invalid field: {key}'}, 400

        db.session.commit()
        return make_response(scientist.to_dict(), 202)

    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id==id).first()
        if not scientist:
            return {'error': 'Scientist not found'}, 404
        db.session.delete(scientist)
        db.session.commit()
        return {}, 204

class Planets(Resource):
    def get(self):
        planets = Planet.query.all()
        planets_dict = [planet.to_dict_2() for planet in planets]
        return make_response(planets_dict, 200)

class Missions(Resource):
    def get(self):
        missions = Mission.query.all()
        missions_dict = [mission.to_dict() for mission in missions]
        return make_response(missions_dict, 200)

    def post(self):
        json_data = request.get_json()
        if not json_data.get('name')or not json_data.get('scientist_id') or not json_data.get('planet_id'):
            return {'errors': ["validation errors"]}, 400
        new_record = Mission(
            name=json_data.get('name'),
            scientist_id=json_data.get('scientist_id'),
            planet_id=json_data.get('planet_id')
        )
        db.session.add(new_record)
        db.session.commit()

        if not new_record.id:
            return {'error': 'Vaidation error'}, 400
        return make_response(new_record.to_dict(),201)


api.add_resource(Home, '/')
api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistById, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5556, debug=True)
