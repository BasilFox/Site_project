from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, SubmitField, EmailField, IntegerField, \
    DateField, TimeField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия пользователя', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    submit = SubmitField('Войти')


class AddForm(FlaskForm):
    event = StringField('Что делаем', validators=[DataRequired()])
    eventplace = StringField('Где собираемся', validators=[DataRequired()])
    eventdate = DateField('Когда: День', format='%Y-%m-%d', validators=[DataRequired()])
    eventtime = TimeField('Когда: Время', validators=[DataRequired()])
    peopleneed = IntegerField('Сколько людей нужно', validators=[DataRequired()])
    peoplehave = IntegerField('Сколько людей идёт', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class EditEventForm(FlaskForm):
    eventplace = StringField('Где собираемся', validators=[DataRequired()])
    eventdate = DateField('Когда: День', format='%Y-%m-%d', validators=[DataRequired()])
    eventtime = TimeField('Когда: Время', validators=[DataRequired()])
    peopleneed = IntegerField('Сколько людей нужно', validators=[DataRequired()])
    submit = SubmitField('Сохранить изменения')
