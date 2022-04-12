from flask import Flask, render_template, redirect, url_for, session, request
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

from data import db_session
from data.meetings import Meeting
from data.users import User
from forms.user import RegisterForm, LoginForm, AddForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/tochka_sbora.sqlite")
login_manager = LoginManager()
login_manager.init_app(app)
user_now = 0


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
@login_required
def index():
    db_session.global_init("db/tochka_sbora.sqlite")
    session = db_session.create_session()
    vstrechy = session.query(Meeting).all()
    orgs = {}
    if current_user.is_authenticated:
        for meet in session.query(Meeting).all():
            for user in session.query(User).filter(User.id == meet.team_leader):
                leader = f'{user.name} {user.surname}'
                orgs[meet.team_leader] = leader
        return render_template('index.html', meetings=vstrechy, names=orgs)
    else:
        form = LoginForm()
        return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    db_session.global_init("db/tochka_sbora.sqlite")
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
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/addevent', methods=['GET', 'POST'])
@login_required
def addevent():
    global user_now
    form = AddForm()
    db_session.global_init("db/tochka_sbora.sqlite")
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        meet = Meeting(
            meeting=form.event.data,
            people_need=form.peopleneed.data,
            people_go=form.peoplehave.data,
            place=form.eventplace.data,
            meet_date=form.eventdate.data,
            meet_time=form.eventtime.data,
            team_leader=user_now
        )
        db_sess.add(meet)
        db_sess.commit()
        return redirect('/index')
    return render_template('add.html', title='Новое событие', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        global user_now
        user_now = user.id
        print(user_now)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.after_request
def redirect_to_sign(response):
    if response.status_code == 401:
        return redirect(url_for('login'))

    return response


@app.route('/admin')
@login_required
def admin():
    return '<h1>Admin page</h1>'


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
