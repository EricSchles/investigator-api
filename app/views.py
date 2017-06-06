from app import app
from app import db
from flask import request, jsonify
from app.models import * #todo - import specific objects
from app.metric_generation import * #todo - import specific objects
from app.visualize_metrics import * #todo - import specific objects
from app.geographic_processing import contains
import json


def to_dict(elem):
    dicter = elem.__dict__
    del dicter["_sa_instance_state"]
    dicter["timestamp"] = str(dicter["timestamp"])
    return dicter

def process_coordinate(elem):
    return elem.rstrip(")").lstrip("(").split("_")
    
@app.route("/api/coordinates/bounding_box/<query>", method=["GET"])
def api_coordinates_bounding_box(query):
    box = [process_coordinate(elem) for elem in query.split(",")]
    lat_box = [elem[0] for elem in box]
    long_box = [elem[1] for elem in box]
    return jsonify({"query_result":[to_dict(elem) for elem in BackpageAdInfo.query.all() if contains(lat_box,long_box,(elem.latitude, elem.longitude))]})
    

@app.route("/api/phone_number/<query>", method=["GET"])
def api_phone_number_query(query):
    return jsonify({"query_result":[to_dict(elem) for elem in BackpageAdInfo.query.filter_by(phone_number=query).all()]})

@app.route("/api/location/<query>", method=["GET"])
def api_location_query(query):
    city,state = query.split(",")
    return jsonify({"query_result":[to_dict(elem) for elem in BackpageAdInfo.query.filter_by(state=state).all() if elem.city == city]})

@app.route("/api/coordinates/<query>", method=["GET"])
def api_coordinates_query(query):
    latitude,longitude = query.split(",")
    return jsonify({"query_result":[to_dict(elem) for elem in BackpageAdInfo.query.filter_by(latitude=latitude).all() if elem.longitude == longitude]})

@app.route("/api/phone_number/all", method=["GET"])
def api_phone_number_all():
    return jsonify({"all_phone_numbers":[elem.phone_number for elem in BackpageAdInfo.query.all()]})

@app.route("/api/coordinates/all", method=["GET"])
def api_coordinates_all():
    return jsonify({"all_coordinates":[(elem.latitude,elem.longitude) for elem in BackpageAdInfo.query.all()]})

@app.route("/api/location/all", method=["GET"])
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

