from flask import Flask, render_template, redirect, make_response
from flask import jsonify
from flask_login import LoginManager, login_user
from flask_restful import Api

from data import db_session
from data import jobs_api, jobs_resource, api_part2
from data.jobs import Jobs
from data.users import User
from forms.user import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/mars_explorer.sqlite")
app.register_blueprint(jobs_api.blueprint)

login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app)
api.add_resource(api_part2.UserListResource, '/api/v2/users')
api.add_resource(api_part2.UserResource, '/api/v2/users/<int:user_id>')
api.add_resource(jobs_resource.JobListResource, '/api/v2/jobs')
api.add_resource(jobs_resource.JobResource, '/api/v2/jobs/<int:job_id>')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():
    db_session.global_init("db/mars_explorer.sqlite")
    session = db_session.create_session()
    raboty = session.query(Jobs).all()
    ekipash = {}
    for job in session.query(Jobs).all():
        for user in session.query(User).filter(User.id == job.team_leader):
            leader = f'{user.name} {user.surname}'
            ekipash[job.team_leader] = leader
    return render_template('index.html', jobs=raboty, names=ekipash)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    db_session.global_init("db/mars_explorer.sqlite")
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)




if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')