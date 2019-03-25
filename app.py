from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab8.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
session = db.session

from models.pokemon import Pokemon

@app.before_first_request
def setup():
    db.Model.metadata.drop_all(bind=db.engine)
    db.Model.metadata.create_all(bind=db.engine)




@app.route('/')
def hello():
    return '<h1>Hello World</h1>'


@app.route('/api/pokemon', methods=['GET'])
def show_all_pokemon():
    query = Pokemon.query.order_by(Pokemon.name.asc())
    start = request.args.get('offset', default=1, type=int)
    num_records = request.args.get('limit', default=10, type=int)
    records = query.paginate(start, num_records).items
    records = list(map(lambda x: x.toDict(), records))
    response = jsonify(records)
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)