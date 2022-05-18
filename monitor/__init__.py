from importlib.resources import Resource
import shelve
import markdown
import os
import shelve
import flask.scaffold
flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func

from flask import Flask, g
from flask_restful import Resource, Api, reqparse
from collections.abc import Mapping

# Create an instance of flask
app = Flask(__name__)

# Create the API
api = Api(app)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("subwaystatus.db")
    return db

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    """
    Present some documentation
    """

    # Open the README file
    with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown_file:
        
        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        return markdown.markdown(content)


class SubwayStatus(Resource):
    def get(self):
        shelf = get_db()
        keys = list(shelf.keys)

        subways = []

        for key in keys:
            subways.append(shelf[key])

        return {'message': 'Success', 'data': subways}, 200

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('identifier', required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('subway_type', required=True)
        parser.add_argument('subway_status', required=True)
        
        # Parse the arguments into an object
        args = parser.parse_args()

        shelf = get_db()
        shelf[args['identifier']] = args

        return {'message': 'Subway registered', 'data': args}, 201

class Subway(Resource):
    def get(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error
        if not (identifier in shelf):
            return {'message': 'Subway not found', 'data': {}}, 404

        return {'message': 'Subway found', 'data': shelf[identifier]}, 200
    
    def delete(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Subway not found', 'data': {}}, 404

        del shelf[identifier]
        return '', 204


api.add_resource(SubwayStatus, '/subways')
api.add_resource(Subway, '/subways/<string:identifier>')