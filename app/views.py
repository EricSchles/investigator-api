from app import app
from app import db
from app import auth
from flask import request, jsonify, abort, g, url_for
from app.models import * #todo - import specific objects
from app.metric_generation import * #todo - import specific objects
from app.visualize_metrics import * #todo - import specific objects
from app.geographic_processing import contains
import json


# How to set up auth for the API
# https://blog.miguelgrinberg.com/post/restful-authentication-with-flask
# https://github.com/miguelgrinberg/REST-auth

@app.route("/", methods=["GET", "POST"])
def index():
    return "Congrats, you've reached investigator's api in order to use the api please visit our docs at: https://github.com/hackingagainstslavery/investigator-api/blob/master/api_docs.md"

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


def to_dict(elem):
    dicter = elem.__dict__
    del dicter["_sa_instance_state"]
    dicter["timestamp"] = str(dicter["timestamp"])
    return dicter

def process_coordinate(elem):
    return elem.rstrip(")").lstrip("(").split("_")


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route("/api/coordinates/bounding_box/<query>", methods=["POST"])
@auth.login_required
def api_coordinates_bounding_box(query):
    box = [process_coordinate(elem) for elem in query.split(",")]
    lat_box = [elem[0] for elem in box]
    long_box = [elem[1] for elem in box]
    return jsonify({"query_result":[to_dict(elem) for elem in BackpageAdInfo.query.all() if contains(lat_box,long_box,(elem.latitude, elem.longitude))]})
    

@app.route("/api/phone_number/<query>", methods=["POST"])
@auth.login_required
def api_phone_number_query(query):
    return jsonify({"query_result":[to_dict(elem) for elem in BackpageAdInfo.query.filter_by(phone_number=query).all()]})

@app.route("/api/location/<query>", methods=["POST"])
@auth.login_required
def api_location_query(query):
    city,state = query.split(",")
    return jsonify({"query_result":[to_dict(elem) for elem in BackpageAdInfo.query.filter_by(state=state).all() if elem.city == city]})

@app.route("/api/coordinates/<query>", methods=["POST"])
@auth.login_required
def api_coordinates_query(query):
    latitude,longitude = query.split(",")
    return jsonify({"query_result":[to_dict(elem) for elem in BackpageAdInfo.query.filter_by(latitude=latitude).all() if elem.longitude == longitude]})

@app.route("/api/phone_number/all", methods=["POST"])
@auth.login_required
def api_phone_number_all():
    return jsonify({"all_phone_numbers":[elem.phone_number for elem in BackpageAdInfo.query.all()]})

@app.route("/api/coordinates/all", methods=["POST"])
@auth.login_required
def api_coordinates_all():
    return jsonify({"all_coordinates":[(elem.latitude,elem.longitude) for elem in BackpageAdInfo.query.all()]})

@app.route("/api/location/all", methods=["GET", "POST"])
@auth.login_required
def api_location_all():
    return jsonify({"all_locations":[(elem.city,elem.state) for elem in BackpageAdInfo.query.all()]})

def to_geojson(coordinates):
    dicter = {}
    dicter["type"] = "Feature"
    dicter["properties"] = {}
    dicter["geometry"] = {
        "type":"Point",
        "coordinates":[float(coordinates[0]), float(coordinates[1])]
        }
    return dicter

