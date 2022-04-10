from flask import jsonify, Flask
from flask_restful import reqparse, abort, Api, Resource

from . import db_session
from .users import User

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('surname', required=True)
parser.add_argument('name', required=True, )
parser.add_argument('age', required=True, type=int)
parser.add_argument('position', required=True, )
parser.add_argument('speciality', required=True, )
parser.add_argument('address', required=True, )
parser.add_argument('email', required=True, )
parser.add_argument('hashed_password', required=True, )


def abort_if_news_not_found(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        abort(404, message=f"User {user_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_news_not_found(user_id)
        session = db_session.create_session()
        news = session.query(User).get(user_id)
        return jsonify({'users': news.to_dict(
            only=('id',
                  'surname',
                  'name',
                  'age',
                  'position',
                  'speciality',
                  'address',
                  'email',
                  'modifed_date',
                  'hashed_password'))})

    def delete(self, user_id):
        abort_if_news_not_found(user_id)
        session = db_session.create_session()
        news = session.query(User).get(user_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email',
                  'modifed_date', 'hashed_password')) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            position=args['position'],
            speciality=args['speciality'],
            address=args['address'],
            email=args['email'],
            hashed_password=['hashed_password']

        )
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
