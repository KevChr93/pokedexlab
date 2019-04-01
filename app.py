import hashlib
import logging
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, make_response, render_template
from sqlalchemy import func
from flask_cors import CORS
from werkzeug.security import safe_str_cmp
from flask_jwt import JWT, jwt_required, current_identity
from logging.handlers import RotatingFileHandler


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab8.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'so unsecured'

# Setting up Logging Functionality (using file-based logging)
logHandler = RotatingFileHandler('info.log', maxBytes=1000, backupCount=1)
logHandler.setLevel(logging.INFO)
app.logger.setLevel(logging.INFO)
app.logger.addHandler(logHandler)
log = app.logger

# enable CORS on all the routes that start with /api
CORS(app, resources={r"/api/*": {"origins": "*"}})

# configure the database to use Flask Sessions
db = SQLAlchemy(app)
session = db.session

# Import the models after initialising the database
from models.pokemon import Pokemon
from models.users import User


def authenticate(username, password):
    """
    The Authenticate function is used primarily by the JWT library to determine if submitted credentials match
    :param username: Unique username for the user
    :param password: Password used to verify user account
    :return: returns an instance of the user model
    """
    try:
        # Fetch user using the username (case insensitive search)
        user = User.query.filter(func.lower(User.username) == func.lower(username)).one_or_none()
        if user:  # If we found a record, then hash password and compare to determine validity
            hashed_password = hashlib.sha1(password.encode('utf-8')).hexdigest()
            if safe_str_cmp(hashed_password, user.password):
                return user  # return the instance of the user
    except Exception as e:
        log.error("Authenticate: {0}".format(e))
    # We failed authentication either due to incorrect credentials or server error
    return False


def identity(payload):
    """
    The identify function will provide a way to retrieve the user details based on the identity in the JWT
    :param payload: the data payload within the JWT request
    :return: returns the serializable (dictionary-based) representation of the user or None if no user found
    """
    try:
        user_id = payload['identity']
        user = User.query.get(user_id)
        if user:
            return user.toDict()
    except Exception as e:
        print(e)
    return None


jwt = JWT(app, authenticate, identity)


@app.before_first_request
def setup():
    print("Running flask for the First Time. Installing database.")
    # db.Model.metadata.drop_all(bind=db.engine)
    db.Model.metadata.create_all(bind=db.engine)


@app.route('/')
def hello():
    records = []
    start = 1
    num_records = 10
    try:
        query = Pokemon.query.order_by(Pokemon.name.asc())
        # retrieve query parameters for controlling amount of records retrieved
        start = request.args.get('offset', default=1, type=int)
        num_records = request.args.get('limit', default=10, type=int)
        # retrieve the data as pages
        records = query.paginate(start, num_records).items
    except Exception as e:
        log.error("Get Index: {0}".format(e))

    return render_template('index.html', pokemon=records, start=start, num_records=num_records )


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/protected')
@app.route('/api/users', methods=['GET'])
def get_users():
    """
    Retrieve the users from the database
    :return:
    """
    try:
        query = User.query.order_by(User.username.asc())
        # retrieve query parameters for controlling amount of records retrieved
        start = request.args.get('offset', default=1, type=int)
        num_records = request.args.get('limit', default=10, type=int)
        # retrieve the data as pages
        records = query.paginate(start, num_records).items
        # convert records into its dictionary-based representation for serialization
        records = [rec.toDict() for rec in records]
        return jsonify(records)  # convert the dictionary-base representation as a JSON response
    except Exception as e:
        log.error("Get Users: {0}".format(e))
        return make_response(jsonify({'error': 'Server encountered an error.'
                                               ' Contact the administrator if problem persists.'}), 500)


@app.route('/protected')
@app.route('/api/users', methods=['POST'])
def store_users():
    try:
        if request.form:  # Check if the user info is submitted by an HTML form
            request_data = request.form
        else:  # Information is submitted via an API request using JSON
            request_data = request.get_json()
        # retrieve the data from the request from the client
        username = request_data.get('username')
        password = request_data.get('password')
        role = request_data.get('role')
        # print("Username: {0}, Password: {1}, Role: {2}".format(username, password, role))
        # If all the information supplied
        if username and password and role:  # (TODO Should provide more extensive data validation before saving)
            # hash the password using the same method used before (TODO put into a function to modularize and DRY method)
            hashed_password = hashlib.sha1(username.encode('utf-8')).hexdigest()
            # Add the data to the model, save and then commit to the database
            user = User(username, hashed_password, role)
            session.add(user)
            session.commit()
            # Once the save operation is completed, then send response with record to the client
            return make_response(jsonify(user.toDict()), 201) # set the HTTP status code to created
        else:
            # At this point, the details submitted by user is incorrect, therefore we sent appropriate HTTP Status code
            return make_response(jsonify({'error': 'Invalid information received.'}), 400)
    except Exception as e:
        log.error("Store Users: {0}".format(e))
        return make_response(jsonify({'error': 'Server encountered an error.'
                                               ' Contact the administrator if problem persists.'}), 500)


@app.route('/api/users/<username>', methods=['GET'])
def get_user_by_username(username):
    """
    A function to retrieve the specific details of a user by the username submitted via the URL
    :param username:
    :return:
    """
    try:
        user = User.query.filter(func.lower(User.username) == func.lower(username)).one_or_none()
        if user:
            return jsonify(user.toDict())
        else:
            return make_response(jsonify(None), 404)
    except Exception as e:
        log.error("Get By Username: {0}".format(e))
        return make_response(jsonify({'error': 'Server encountered an error.'
                                               ' Contact the administrator if problem persists.'}), 500)


@app.route('/api/pokemon', methods=['GET'])
def show_all_pokemon():
    try:
        query = Pokemon.query.order_by(Pokemon.name.asc())
        # retrieve query parameters for controlling amount of records retrieved
        start = request.args.get('offset', default=1, type=int)
        num_records = request.args.get('limit', default=10, type=int)
        # retrieve the data as pages
        records = query.paginate(start, num_records).items
        # convert records into its dictionary-based representation for serialization using the map function
        records = list(map(lambda x: x.toDict(), records))  # convert to list as is needed to be converted to JSON
        return jsonify(records)

    except Exception as e:
        log.error("Show all Pokemon: {0}".format(e))
        return make_response(jsonify({'error': 'Server encountered an error.'
                                               ' Contact the administrator if problem persists.'}), 500)


@app.route('/api/pokemon/<pk_id>')
def get_pokemon_by_id(pk_id):
    try:
        pokemon = Pokemon.query.get(pk_id)
        if pokemon:
            return jsonify(pokemon.toDict())
        else:
            results = None
            return make_response(jsonify(results), 404)
    except Exception as e:
        log.error("Get Pokemon by Id: {0}".format(e))
        return make_response(jsonify({'error': 'Server encountered an error.'
                                               ' Contact the administrator if problem persists.'}), 500)


@app.route('/api/pokemon/type', methods=['GET'])
def get_all_pokemon_type():
    try:
        # Attempt to retrieve distinct values from the 'type_1' column in the Pokemon table
        records = db.session.query(Pokemon.type_1).distinct().all()  # https://docs.sqlalchemy.org/en/latest/orm/query.html#distinct
        # convert records into its dictionary-based representation for serialization using the map function
        records = list(map(lambda x: x[0], records))
        # send data as JSON to requesting client
        return jsonify(records)
    except Exception as e:
        log.error("Get All Pokemon Type: {0}".format(e))
        return make_response(jsonify({'error': 'Server encountered an error.'
                                               ' Contact the administrator if problem persists.'}), 500)


@app.route('/api/pokemon/type/<type_1>', methods=['GET'])
def get_pokemon_by_type(type_1):
    try:
        query = Pokemon.query.filter(func.lower(Pokemon.type_1) == func.lower(type_1))
        query = query.order_by(Pokemon.name.asc())
        # retrieve query parameters for controlling amount of records retrieved
        start = request.args.get('offset', default=1, type=int)
        num_records = request.args.get('limit', default=10, type=int)
        # retrieve the data as pages
        records = query.paginate(start, num_records).items
        records = [rec.toDict() for rec in records]  # conversion to dictionary-based representation
        return jsonify(records)  # serialization to JSON
    except Exception as e:
        log.error("Get Pokemon by identified type: {0}".format(e))
        return make_response(jsonify({'error': 'Server encountered an error.'
                                               ' Contact the administrator if problem persists.'}), 500)


if __name__ == "__main__":
    print("Running From the Command line")
    app.run(host='0.0.0.0', debug=True, use_reloader=True)
