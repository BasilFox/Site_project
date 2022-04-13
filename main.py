import os

import requests
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

from data import db_session
from data.meetings import Meeting
from data.peoplego import Iamgo
from data.users import User
from forms.user import RegisterForm, LoginForm, AddForm, EditEventForm

imgdir = os.path.join('http://127.0.0.1:8080', 'static', 'img')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = imgdir
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
    title = 'Точка сбора!'
    if current_user.is_authenticated:
        for meet in session.query(Meeting).all():
            for user in session.query(User).filter(User.id == meet.team_leader):
                leader = f'{user.name} {user.surname}'
                orgs[meet.team_leader] = leader
        return render_template('index.html', meetings=vstrechy, names=orgs, title=title)
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
            team_leader=current_user.id
        )

        db_sess.add(meet)
        db_sess.commit()
        print(meet.id)
        db_session.global_init("db/tochka_sbora.sqlite")
        go = Iamgo(user_id=current_user.id,
                   meet_id=meet.id)
        db_sess.add(go)
        db_sess.commit()
        toponym_to_find = meet.place

        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_to_find,
            "format": "json"}
        response1 = requests.get(geocoder_api_server, params=geocoder_params).json()
        json_response = response1
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        server = "http://static-maps.yandex.ru/1.x"
        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
        params = {
            'll': ','.join([toponym_longitude, toponym_lattitude]),
            'z': 17,
            'l': 'map',
            "pt": f"{toponym_longitude},{toponym_lattitude},pm2dbl"
        }
        response = requests.get(server, params=params)
        if response:
            map_file = f"static/img/{meet.id}.jpg"
            with open(map_file, "wb") as file:
                file.write(response.content)
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


@app.route('/event/<eventnum>')
@login_required
def eventview(eventnum):
    db_session.global_init("db/tochka_sbora.sqlite")
    session = db_session.create_session()
    vstrechy = session.query(Meeting).filter(Meeting.id == eventnum).all()
    peoplego = session.query(Iamgo).filter(Iamgo.meet_id == eventnum).all()
    orgs = {}
    people = []
    image = ''
    leaderid = 0
    title = ''
    flag = False
    if current_user.is_authenticated:
        for meet in session.query(Meeting).filter(Meeting.id == eventnum).all():
            for user in session.query(User).filter(User.id == meet.team_leader):
                leader = f'{user.name} {user.surname}'
                orgs[meet.team_leader] = leader
                leaderid = meet.team_leader
                title = meet.meeting
                image = os.path.join(app.config['UPLOAD_FOLDER'], f'{meet.id}.jpg')
        for user in peoplego:
            if user.user_id == current_user.id:
                flag = True
            for id in session.query(User).filter(User.id == user.user_id):
                man = f'{id.name} {id.surname}'
                people.append(man)
        return render_template('showevent.html', meetings=vstrechy, names=orgs, competitors=people,
                               image=image, leaderid=leaderid, current_user=current_user.id,
                               title=title, flag=flag)
    else:
        form = LoginForm()
        return render_template('login.html', title='Авторизация', form=form)


@app.route('/delete/<eventnum>')
@login_required
def delete(eventnum):
    db_session.global_init("db/tochka_sbora.sqlite")
    session = db_session.create_session()
    id_fordel = eventnum
    event = (session.query(Meeting).filter(Meeting.id == eventnum).all()[0]).meeting
    if current_user.is_authenticated:
        return render_template('delete.html', eventid=id_fordel, event=event)
    else:
        form = LoginForm()
        return render_template('login.html', title='Авторизация', form=form, )


@app.route('/realdelete/<eventnum>')
@login_required
def realdelete(eventnum):
    db_session.global_init("db/tochka_sbora.sqlite")
    session = db_session.create_session()
    id_fordel = eventnum

    if current_user.is_authenticated:
        session.query(Meeting).filter(Meeting.id == eventnum).delete()
        session.query(Iamgo).filter(Iamgo.meet_id == eventnum).delete()
        session.commit()
        os.remove(f'static/img/{id_fordel}.jpg')
        return render_template('deletesuc.html', eventid=id_fordel)
    else:
        form = LoginForm()
        return render_template('login.html', title='Авторизация', form=form, )


@app.route('/edit/<eventnum>', methods=['GET', 'POST'])
@login_required
def edit(eventnum):
    db_session.global_init("db/tochka_sbora.sqlite")
    session = db_session.create_session()
    id_fordel = eventnum
    form = EditEventForm()
    if form.validate_on_submit():
        session.query(Meeting).filter(Meeting.id == eventnum).update(
            {Meeting.place: form.eventplace.data, Meeting.meet_date: form.eventdate.data,
             Meeting.meet_time: form.eventtime.data, Meeting.people_need: form.peopleneed.data})
        session.commit()
        os.remove(f'static/img/{id_fordel}.jpg')
        meet = session.query(Meeting).filter(Meeting.id == eventnum).first()
        toponym_to_find = meet.place

        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_to_find,
            "format": "json"}
        response1 = requests.get(geocoder_api_server, params=geocoder_params).json()
        json_response = response1
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        server = "http://static-maps.yandex.ru/1.x"
        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
        params = {
            'll': ','.join([toponym_longitude, toponym_lattitude]),
            'z': 17,
            'l': 'map',
            "pt": f"{toponym_longitude},{toponym_lattitude},pm2dbl"
        }
        response = requests.get(server, params=params)
        if response:
            map_file = f"static/img/{meet.id}.jpg"
            with open(map_file, "wb") as file:
                file.write(response.content)
        return redirect('/index')

    return render_template('edit.html', eventid=id_fordel, form=form)


@app.route('/iamgo/<eventnum>', methods=['GET', 'POST'])
@login_required
def iamgo(eventnum):
    db_session.global_init("db/tochka_sbora.sqlite")
    session = db_session.create_session()
    id_fordel = eventnum
    if current_user.is_authenticated:
        session.query(Meeting).filter(Meeting.id == eventnum).update(
            {Meeting.people_go: Meeting.people_go + 1})
        event = Iamgo()
        event.user_id = current_user.id
        event.meet_id = id_fordel
        session.add(event)
        session.commit()
        return redirect(f'/event/{id_fordel}')


@app.route('/iamnotgo/<eventnum>', methods=['GET', 'POST'])
@login_required
def ianotmgo(eventnum):
    db_session.global_init("db/tochka_sbora.sqlite")
    session = db_session.create_session()
    id_fordel = eventnum
    if current_user.is_authenticated:
        session.query(Iamgo).filter(Iamgo.user_id == current_user.id,
                                    Iamgo.meet_id == eventnum).delete()
        session.query(Meeting).filter(Meeting.id == eventnum).update(
            {Meeting.people_go: Meeting.people_go - 1})

        session.commit()
        return redirect(f'/event/{id_fordel}')
@app.route('/myevents', methods=['GET', 'POST'])
@login_required
def myevents():
    db_session.global_init("db/tochka_sbora.sqlite")
    session = db_session.create_session()
    id_fordel = current_user.id
    events = session.query(Iamgo).filter(Iamgo.user_id == id_fordel).all()
    print(list(events))
    sp =[]
    if current_user.is_authenticated:
        for event in events:
            sp.append(event.meet_id)

            session.commit()
        return render_template('myevents.html', title='Мои события.', sp=sp )

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
