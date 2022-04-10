from flask import jsonify, Flask
from flask_restful import reqparse, abort, Api, Resource

from . import db_session
from .jobs import Jobs

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('job', required=True)
parser.add_argument('work_size', required=True, type=int)
parser.add_argument('collaborators', required=True, )
parser.add_argument('is_finished', required=True, type=bool)
parser.add_argument('team_leader', required=True, type=int)


def abort_if_news_not_found(job_id):
    session = db_session.create_session()
    jobs = session.query(Jobs).get(job_id)
    if not jobs:
        abort(404, message=f"User {job_id} not found")


class JobResource(Resource):
    def get(self, job_id):
        abort_if_news_not_found(job_id)
        session = db_session.create_session()
        news = session.query(Jobs).get(job_id)
        return jsonify({'jobs': news.to_dict(
            only=('id',
                  'job',
                  'work_size',
                  'collaborators',
                  'start_date',
                  'end_date',
                  'is_finished',
                  'team_leader',))})

    def delete(self, job_id):
        abort_if_news_not_found(job_id)
        session = db_session.create_session()
        news = session.query(Jobs).get(job_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class JobListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'job': [item.to_dict(
            only=('id',
                  'job',
                  'work_size',
                  'collaborators',
                  'start_date',
                  'end_date',
                  'is_finished',
                  'team_leader')) for item in jobs]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        job = Jobs(
            job=args['job'],
            work_size=args['work_size'],
            collaborators=args['collaborators'],
            is_finished=args['is_finished'],
            team_leader=args['team_leader'],

        )
        session.add(job)
        session.commit()
        return jsonify({'success': 'OK'})
