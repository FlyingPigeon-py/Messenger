import json
from datetime import datetime as dt

import flask
from flask import jsonify, request
from flask_login import current_user

from data import db_session
from data.chat import Chat
from data.users import User

blueprint = flask.Blueprint(
    'api',
    __name__,
    template_folder='templates'
)

db_session.global_init("db/messenger.db")
db_sess = db_session.create_session()


def get_last_messeg_time(chat):
    text = json.loads(chat.messages)
    if text:
        return dt.strptime(text[-1]["time"], "%Y/%m/%d/ %H:%M:%S")


def get_privats():
    chats = json.loads(current_user.chats)
    new_session = db_session.create_session()
    chats = new_session.query(Chat).filter(Chat.id.in_(chats))
    new_session.close()
    chats = filter(lambda chat: chat.isPrivate, chats)
    return chats


def get_current_time():
    return str(dt.now().strftime("%Y/%m/%d/ %H:%M:%S"))


def get_chat_img(chat):
    if chat.isPrivate:
        user_id = list(filter(lambda user_id: user_id != current_user.id, map(int, chat.members.split(","))))
        user = db_sess.query(User).get(user_id[0])
        return user.img
    else:
        return chat.img


def get_chat_name(chat):
    if chat.isPrivate:
        user_id = list(filter(lambda user_id: user_id != current_user.id, map(int, chat.members.split(","))))
        user = db_sess.query(User).get(user_id[0])
        return user.name
    else:
        return chat.name


def get_chat_id(chat):
    if chat.isPrivate:
        user_id = list(filter(lambda user_id: user_id != current_user.id, map(int, chat.members.split(","))))
        user = db_sess.query(User).get(user_id[0])
        return user.id
    else:
        return chat.id


def get_last_messege(chat):
    text = json.loads(chat.messages)
    if text:
        return text[-1]["text"]
    else:
        return ""


def get_url_img(url):
    # if validators.url(url):
    return url
    # else:
    #     return "https://www.meme-arsenal.com/memes/ccd0c24ed30b3293b72c019930babe38.jpg"


def del_member(chat_id, user_id):
    chat = db_sess.query(Chat).get(chat_id)
    members = filter(lambda member: member != user_id, map(int, chat.members.split(',')))
    chat.members = ",".join(map(str, members))
    user = db_sess.query(User).get(user_id)
    chats = [j for j in json.loads(user.chats) if j != chat_id]
    user.chats = json.dumps(chats)
    db_sess.commit()


def private_chat_for_user(user_id):
    chats = json.loads(current_user.chats)
    chats = db_sess.query(Chat).filter(Chat.id.in_(chats))
    chats = list(
        filter(lambda chat: chat.isPrivate and user_id in map(int, chat.members.split(",")), chats))
    if chats:
        return chats[0].id
    else:
        return 0


@blueprint.route('/api/find_private_chat/<int:user_id>', methods=['POST', "GET"])
def find_private_chat(user_id):
    ans = private_chat_for_user(user_id)
    return jsonify({'data': ans})


@blueprint.route('/api/get_private_chats', methods=['POST', "GET"])
def send_private_chats():
    chats = get_privats()
    html = """
            <p style="color: azure; overflow: hidden; font-size: 16px; margin-left: 10px; margin-bottom: 10px">
                <ion-icon name="add-circle"></ion-icon>
                Create Chat
            </p>
            <input autocomplete="off" class="field_text" type="text" name="name-chat" id="name-chat"
                       placeholder="Название чата" value="">
            """

    for chat in chats:
        user_id = list(filter(lambda user_id: user_id != current_user.id, map(int, chat.members.split(","))))
        if user_id:
            user = db_sess.query(User).get(user_id[0])
            html += f"""
            <div class="form_radio_btn">
                <input id="{user.id}" name="{user.id}" type="checkbox" value="{user.id}">
                    <label for="{user.id}">
                    <img class="chat_icon"
                        src="{user.img}">
                    <p style="overflow: hidden; font-size: 17px;">{user.name}</p>
                </label>
            </div>
            """

    return jsonify({'data': html})


# @blueprint.route('/api/send_messages/<int:chat_id>/<int:user_id>/<string:text>', methods=['POST', "GET"])
# def send_message(chat_id, user_id, text):
#     chat = db_sess.query(Chat).get(chat_id)
#     messages = json.loads(chat.messages)
#
#     messages.append({"user_id": user_id, "text": text, "time": get_current_time()})
#     chat.messages = json.dumps(messages)
#     db_sess.commit()
#     db_sess.close()
#     return '200'


@blueprint.route('/api/send_messages', methods=['POST', "GET"])
def send_message():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['text', 'chat_id', 'user_id']):
        return jsonify({'error': 'Bad request'})

    chat = db_sess.query(Chat).get(int(request.json['chat_id']))
    messages = json.loads(chat.messages)

    messages.append({"user_id": int(request.json['user_id']), "text": request.json['text'], "time": get_current_time()})
    chat.messages = json.dumps(messages)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/get_messages/<int:chat_id>', methods=['GET'])
def get_text(chat_id):
    chat = db_sess.query(Chat).get(chat_id)
    if chat:
        messages = json.loads(chat.messages)
        text = ''
        last_athor = ''
        user = None
        for message in messages:
            if message["text"]:
                if message["user_id"] == current_user.id:
                    if last_athor != message["user_id"]:
                        last_athor = current_user.id
                        text += f"""
                                <div style="display: flex; font-family: monospace;">
                                    <div class="self_messege" style="margin-right: 0px">
                                        <p style="font-family: monospace;">
                                            {message["text"]}
                                        </p>
                                        <p class="time_messege" align="right" align="justify">{':'.join(message["time"].split()[-1].split(':')[:2])}</p>
                                    </div>
                                    <img class="self_user_icon"
                                        src={current_user.img}>
                                </div>
                                """
                    else:
                        last_athor = current_user.id
                        text += f"""
                                <div style="display: flex; font-family: monospace;">
                                    <div class="self_messege" style="border-radius: 20px 20px 20px 20px;">
                                        <p style="font-family: monospace;">
                                            {message["text"]}
                                        </p>
                                        <p class="time_messege" align="right" align="justify">{':'.join(message["time"].split()[-1].split(':')[:2])}</p>
                                    </div>
                                </div>
                                """
                else:
                    if last_athor == message["user_id"]:
                        last_athor = message["user_id"]
                        text += f"""
                        <div>
                        <div class="other_messege">
                            {message["text"]}
                            <p class="time_messege" align="right">{':'.join(message["time"].split()[-1].split(':')[:2])}</p>
                        </div>
                        </div>
                        """
                    else:
                        new_session = db_session.create_session()
                        user = new_session.query(User).get(message["user_id"])
                        new_session.close()

                        last_athor = message["user_id"]
                        text += f"""
                        <div>
                        <img class="other_user_icon" style='float:left'
                            src={user.img}>
                        <div class="other_messege" style="margin-left: 0px">
                            <p class="athor_messege">{user.name}</p>
                            {message["text"]}
                            <p class="time_messege" align="right">{':'.join(message["time"].split()[-1].split(':')[:2])}</p>
                        </div>
                        </div>
                        """
        return jsonify({'data': text})
    return jsonify('404')


@blueprint.route('/api/get_settings_add_members_html/<int:chat_id>', methods=['GET', 'POST'])
def members_add_chat_html(chat_id):
    chat = db_sess.query(Chat).get(chat_id)
    members = list(map(int, chat.members.split(',')))

    privates = [i for i in get_privats() if get_chat_id(i) not in members]

    html = """<div style="margin-bottom: 20px; margin-left: 0px">
            <ion-icon name="person-add"></ion-icon>
            </ion-icon> Addition

            <button class="chat_settings" style="margin-left: 55%; font-size: 16px" href="#"
                    onclick="OnOffAddMember()">
                Back
            </button>
        </div>"""

    for user in privates:
        html += f"""
            <div class="form_chat_btn">
            <img class="chat_icon"
                 src="{get_chat_img(user)}">
            <p style="overflow: hidden; font-size: 17px;">{get_chat_name(user)}</p>
            <button class="chat_member_button_add" onclick="AddUserInChat({chat_id}, {get_chat_id(user)})">
                <ion-icon name="add"></ion-icon>
            </button>
        </div>"""

    return jsonify({'data': html})


@blueprint.route('/api/get_settings_members_html/<int:chat_id>', methods=['GET', 'POST'])
def members_chat_html(chat_id):
    chat = db_sess.query(Chat).get(chat_id)
    members = map(int, chat.members.split(","))

    new_session = db_session.create_session()
    members = new_session.query(User).filter(User.id.in_(members)).all()
    new_session.close()

    owner = chat.owner_id
    html = ""
    if not chat.isPrivate:
        if owner == current_user.id:
            html = """<div style="margin-bottom: 20px; margin-left: 0px">
                        <ion-icon name="people"></ion-icon>
                        Members
            
                        <button class="chat_settings" style="margin-left: 49%; font-size: 16px" href="#"
                                onclick="OnOffAddMember()">
                            <ion-icon name="person-add"></ion-icon>
                            add
                        </button>
                   </div>"""
        if owner != current_user.id:
            html = """<div style="margin-bottom: 20px; margin-left: 0px">
                        <ion-icon name="people"></ion-icon>
                        Members
                   </div>"""
    else:
        html = """<div style="margin-bottom: 20px; margin-left: 0px">
                        <ion-icon name="people"></ion-icon>
                        Members
                   </div>"""

    for user in members:
        if user.id != current_user.id:
            if user.id == owner:
                name = user.name + '<ion-icon name="ribbon-outline"></ion-icon>'
            else:
                name = user.name
            if owner == current_user.id:
                html += f"""                        
                    <div class="form_chat_btn">
                    <img class="chat_icon"
                         src="{user.img}">
                    <p style="overflow: hidden; font-size: 17px;">{name}</p>
                    <button class="chat_member_button" href="#" onclick="RedirectToUser({user.id})">
                        <ion-icon name="chatbubble-ellipses"></ion-icon>
                    </button>
                    <button class="chat_member_button_del" onclick="DeleteUserFromChat({chat.id}, {user.id})">
                        <ion-icon name="close"></ion-icon>
                    </button>
                </div>"""
            else:
                html += f"""                        
                    <div class="form_chat_btn">
                    <img class="chat_icon"
                         src="{user.img}">
                    <p style="overflow: hidden; font-size: 17px;">{name}</p>
                    <button class="chat_member_button" href="#" onclick="RedirectToUser({user.id})">
                        <ion-icon name="chatbubble-ellipses"></ion-icon>
                    </button>
                </div>"""

    return jsonify({'data': html})


@blueprint.route('/api/get_settings_header/<int:chat_id>', methods=['GET', 'POST'])
def get_settings_info(chat_id):
    chat = db_sess.query(Chat).get(chat_id)
    img = get_chat_img(chat)
    name = get_chat_name(chat)
    func = ""
    if current_user.id == chat.owner_id:
        if not chat.isPrivate:
            func = "OnOffChatImg()"
    html = f"""
        <dic id="back_img" class="back_ground_chat_img"
                     style="background-image: url('{img}');">
        <div class="chat_info_bar">
            <img id="chat_img_set" onclick="{func}" class="chat_icon_bar"
                 src="{img}">
            <div>
                <input id="chat_title" value="{name}" maxlength=12 type="text" class="chat_name_inp"
                       style="overflow: hidden; font-size: 30px; margin: 10px">
            </div>


            <button class="chat_leave" style="margin-right: 20px" href="#" onclick="DeleteChat()">
                <ion-icon name="exit" size="large"></ion-icon>
            </button>
        </div>
        </div>
    """

    return jsonify({'data': html})


@blueprint.route('/api/get_settings_info/<int:chat_id>', methods=['GET', 'POST'])
def get_settings_header(chat_id):
    chat = db_sess.query(Chat).get(chat_id)
    count_members = len(chat.members.split(','))
    count_messages = len(json.loads(chat.messages))

    html = f"""
        <p>
            <ion-icon name="person"></ion-icon>
            Members: {count_members}
        </p>
        <p>
            <ion-icon name="chatbubbles"></ion-icon>
            Messages: {count_messages}
        </p>
    """

    return jsonify({'data': html})


@blueprint.route('/api/get_header/<int:chat_id>', methods=['GET', 'POST'])
def header(chat_id):
    chat = db_sess.query(Chat).get(chat_id)
    chat_img = get_chat_img(chat)
    char_name = get_chat_name(chat)
    members_count = "" if chat.isPrivate else str(len(chat.members.split(','))) + " members"
    members = f'<p class="last_messege">{members_count}</p>' if not chat.isPrivate else ""
    if chat:
        text = f"""
            <img class="chat_icon"
                src={chat_img}>
            <div>
                <p>{char_name}</p>
                {members}
            </div>
        
            <button class="chat_settings" href="#" onclick="OnOffChatSettings()">
                <ion-icon name="ellipsis-vertical" size="large"></ion-icon>
                </ion-icon></button>
        """

        return jsonify({'data': text})

    return jsonify('404')


@blueprint.route('/api/user_add_chat/<int:chat_id>', methods=['POST', 'GET'])
def user_add_chat(chat_id):
    user = db_sess.query(User).get(current_user.id)
    if user.chats:
        chats = json.loads(user.chats)
        chats.append(chat_id)
        user.chats = json.dumps(chats)
    else:
        user.chats = json.dumps([chat_id])
    db_sess.commit()
    return "200"


@blueprint.route('/api/user_add_in_chat/<int:chat_id>/<int:user_id>', methods=['POST', 'GET'])
def user_add_in_chat(chat_id, user_id):
    user = db_sess.query(User).get(user_id)
    if user.chats:
        chats = json.loads(user.chats)
        chats.append(chat_id)
        user.chats = json.dumps(chats)
    else:
        user.chats = json.dumps([chat_id])

    chat = db_sess.query(Chat).get(chat_id)
    chat.members = chat.members + f",{user_id}"
    db_sess.commit()
    return "200"


@blueprint.route('/api/add_chat_v/<string:name>/<string:img>/<string:members>/<int:isPr>/<int:cui>',
                 methods=['POST', 'GET'])
def add_chat_v(name, img, members, isPr, cui):
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

    chat_id = chat.id
    db_sess.commit()
    return jsonify({'data': chat_id})


@blueprint.route('/api/add_chat/<string:name>/<string:img>/<string:members>/<int:isPr>/<int:cui>',
                 methods=['POST', 'GET'])
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


@blueprint.route('/api/user_chats', methods=['GET'])
def chats_for_user():
    user = current_user
    html = ""

    if user.chats:

        chats = db_sess.query(Chat).filter(Chat.id.in_(json.loads(user.chats)))
        chats = sorted(chats, key=lambda x: get_last_messeg_time(x), reverse=True)
        for chat in chats:
            chat_img = get_chat_img(chat)
            char_name = get_chat_name(chat)
            last_messege = get_last_messege(chat)
            html += f'''
            <button class="chat_btn" onclick="OpenChat({chat.id})">
                <div class="chat">
                    <img class="chat_icon"
                        src={chat_img}>
                    <div>
                        <p style="overflow: hidden;">{char_name}</p>
                        <p class="last_messege">{last_messege}</p>
                    </div>
                </div>
            </button>
            '''
        return jsonify(
            {
                'data': html
            }
        )
    return '404'


@blueprint.route('/api/change_img', methods=['GET', 'POST'])
def change_img():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['img']):
        return jsonify({'error': 'Bad request'})
    user = db_sess.query(User).get(current_user.id)
    user.img = request.json['img']
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/change_img_chat', methods=['GET', 'POST'])
def change_chat_img():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['img', 'name', 'chat_id']):
        return jsonify({'error': 'Bad request'})
    chat = db_sess.query(Chat).get(request.json['chat_id'])
    if not chat.isPrivate:
        if current_user.id == chat.owner_id and (request.json['img'] != '' or request.json['name'] != ''):
            if request.json['img'] != '':
                chat.img = request.json['img']
            if request.json['name'] != '':
                chat.name = request.json['name']
            db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/get_img', methods=['GET'])
def current_img():
    return jsonify(
        {
            'data': current_user.img
        }
    )


@blueprint.route('/api/delete_chat/<int:chat_id>', methods=['POST', 'GET'])
def delete_chat(chat_id):
    chat = db_sess.query(Chat).get(chat_id)
    if current_user.id == chat.owner_id or chat.isPrivate:
        for i in chat.members.split(","):
            try:
                user = db_sess.query(User).get(i)
                chats = [j for j in json.loads(user.chats) if j != chat_id]
                user.chats = json.dumps(chats)
            except Exception as err:
                print(err)
        db_sess.delete(chat)
        db_sess.commit()
        return "200"
    else:
        return "300"


@blueprint.route('/api/leave_chat/<int:chat_id>', methods=['POST', 'GET'])
def leave_chat(chat_id):
    chat = db_sess.query(Chat).get(chat_id)

    if not chat.isPrivate:
        if current_user.id != chat.owner_id:
            del_member(chat_id, current_user.id)
        elif current_user.id == chat.owner_id:
            delete_chat(chat_id)
    elif chat.isPrivate:
        delete_chat(chat_id)
    return "200"


@blueprint.route('/api/delete_member_from_chat/<int:chat_id>/<int:user_id>', methods=['POST', 'GET'])
def delete_member_from_chat(chat_id, user_id):
    del_member(chat_id, user_id)
    return "200"


@blueprint.route('/api/change_bg_img', methods=['GET', 'POST'])
def change_bg_img():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['img']):
        return jsonify({'error': 'Bad request'})

    user_id = current_user.id
    user = db_sess.query(User).get(user_id)
    user.past_background = user.current_background
    user.current_background = request.json['img']
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/chats_count', methods=['POST', 'GET'])
def chats_count():
    count = len(json.loads(current_user.chats))
    return jsonify({'data': count})
