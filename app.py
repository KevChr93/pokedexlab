import hashlib
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, make_response
from sqlalchemy import func
from flask_cors import CORS
from werkzeug.security import safe_str_cmp
from flask_jwt import JWT, jwt_required, current_identity

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab8.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'so unsecured'

# enable CORS on all the routes that start with /api
CORS(app, resources={r"/api/*": {"origins": "*"}})

# configure the database to use Flask Sessions
db = SQLAlchemy(app)
session = db.session

# Import the models after initialising the database
from models.pokemon import Pokemon
from models.users import User


def authenticate(username, password):
    try:
        user = User.query.filter(func.lower(User.username) == func.lower(username)).one_or_none()
        if user:
            hashed_password = hashlib.sha1(password.encode('utf-8')).hexdigest()
            if safe_str_cmp(hashed_password, user.password):
                return user
    except Exception as e:
        print(e)

    return False


def identity(payload):
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
    # db.Model.metadata.drop_all(bind=db.engine)
    db.Model.metadata.create_all(bind=db.engine)


@app.route('/')
def hello():
    return '<h1>Hello World</h1>'


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        query = User.query.order_by(User.username.asc())
        start = request.args.get('offset', default=1, type=int)
        num_records = request.args.get('limit', default=10, type=int)
        records = query.paginate(start, num_records).items
        records = [rec.toDict() for rec in records]
        response = jsonify(records)
        return response
    except Exception as e:
        print(e)
        return make_response(jsonify({'error': 'Server encountered an error. Contact administrator'}), 500)


@app.route('/api/users/<username>', methods=['GET'])
def get_user_by_username(username):
    try:
        user = User.query.filter(func.lower(User.username) == func.lower(username)).one_or_none()
        if user:
            return jsonify(user.toDict())
        else:
            return make_response(jsonify(None), 404)
    except Exception as e:
        print(e)
        return make_response(jsonify({'error': 'Server encountered an error. Contact administrator'}), 500)


@app.route('/api/pokemon', methods=['GET'])
def show_all_pokemon():
    try:
        query = Pokemon.query.order_by(Pokemon.name.asc())

        start = request.args.get('offset', default=1, type=int)
        num_records = request.args.get('limit', default=10, type=int)

        records = query.paginate(start, num_records).items
        records = list(map(lambda x: x.toDict(), records))
        response = jsonify(records)
        return response

    except Exception as e:
        print(e)
        return make_response(jsonify({'error': 'Server encountered an error. Contact administrator'}), 500)


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
        print(e)
        return make_response(jsonify({'error': 'Server encountered an error. Contact administrator'}), 500)


@app.route('/api/pokemon/type', methods=['GET'])
def get_all_pokemon_type():
    try:
        # https://docs.sqlalchemy.org/en/latest/orm/query.html#distinct
        records = db.session.query(Pokemon.type_1).distinct().all()
        records = list(map(lambda x: x[0], records))
        response = jsonify(records)
        return response
    except Exception as e:
        print(e)
        return make_response(jsonify({'error': 'Server encountered an error. Contact administrator'}), 500)


@app.route('/api/pokemon/type/<type_1>', methods=['GET'])
def get_pokemon_by_type(type_1):
    try:
        query = Pokemon.query.filter(func.lower(Pokemon.type_1) == func.lower(type_1))
        query = query.order_by(Pokemon.name.asc())

        start = request.args.get('offset', default=1, type=int)
        num_records = request.args.get('limit', default=10, type=int)

        records = query.paginate(start, num_records).items
        records = [rec.toDict() for rec in records]
        response = jsonify(records)
        return response
    except Exception as e:
        print(e)
        return make_response(jsonify({'error': 'Server encountered an error. Contact administrator'}), 500)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
