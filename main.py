import json

import requests
from flask import render_template, Flask, redirect, request
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

from datetime import datetime as dt
from waitress import serve
import api
from data import db_session
from data.chat import Chat
from data.users import User
from forms import LoginForm, RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/messenger.db")
db_sess = db_session.create_session()
app.register_blueprint(api.blueprint)


def get_current_time():
    return str(dt.now().strftime("%Y/%m/%d/ %H:%M:%S"))


def add_chat(name, img, members, isPr, cui):
    isPr = True if isPr == 1 else False
    chat = Chat(
        name=name,
        owner_id=cui,
        img="https://otkritkis.com/wp-content/uploads/2021/11/anim-avatar-discord-29.gif",
        members=str(cui) + ',' + members,
        messages=json.dumps([{'user_id': 1, 'text': '', 'time': get_current_time()}]),
        isPrivate=bool(isPr)
    )

    db_sess.add(chat)
    db_sess.commit()

    for i in members.split(',') + [cui]:
        try:
            user = db_sess.query(User).get(int(i))
            chats = json.loads(user.chats)
            chats.append(chat.id)
            user.chats = json.dumps(chats)
        except Exception as err:
            pass

    db_sess.commit()
    return "200"

@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route('/')
def index():
    return redirect('/login')


@app.route('/messenger', methods=['GET', 'POST'])
@login_required
def messenger():
    if request.method == 'POST':

        if "name-chat" in request.form:
            name = request.form["name-chat"]
            members = [i for i in request.form if i != "name-chat"]
            if members:
                add_chat(name, 'none', ','.join(members), 0, current_user.id)
            # requests.post(f"/api/add_chat/{name}/none/{)}/0/{current_user.id}")

        elif "user-email" in request.form:
            user = db_sess.query(User).filter(User.email == request.form['user-email']).first()

            if user and user.id != current_user.id:
                # requests.post(f"/api/add_chat/privat_chat/non/{user.id}/1/{current_user.id}")
                add_chat('private_chat', 'none', str(user.id), 1, current_user.id)
        return redirect('/messenger')
    else:
        return render_template('messenger3.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
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
            name=form.name.data,
            email=form.email.data,
            chats=json.dumps([]),
            img="https://cdn-icons-png.flaticon.com/512/7710/7710521.png"
        )

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    try:
        if current_user.id:
            return redirect("/messenger")
    except AttributeError:
        pass
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/messenger")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)

    return render_template('login.html', form=form)


if __name__ == '__main__':
    # app.run(port=5000, host='0.0.0.0')
    serve(app, port=5000, host='0.0.0.0')