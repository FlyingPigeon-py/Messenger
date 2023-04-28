const add_chat = document.getElementById("add_btn");
const add_chats = document.getElementById("add_chats");
const chats = document.getElementById("chats");
const settings = document.getElementById("settings");
const messeges = document.getElementById("messeges");
const profile = document.getElementById("profile");
const chat = document.getElementById("chat_id");
const chat_header = document.getElementById("chat_header");
const profile_img = document.getElementById("profile_img");
const private_chats = document.getElementById("private_chats");
const chat_settings_bar = document.getElementById("chat_settings_bar");
const img_div = document.getElementById("img_div");
const members_div = document.getElementById("members_div");
const chat_img = document.getElementById("chat_img_sel");
const chat_img_set = document.getElementById("chat_img_set");
const back_img = document.getElementById("back_img");
const add_member_div = document.getElementById("add_member_div");
const settings_header_bar = document.getElementById("settings_header_bar");
const input_messege_bar = document.getElementById("input_message_bar");
const godown = document.getElementById("godown");
const chats_count = document.getElementById("chats_count");


function LoadChatsCount(){
    $.ajax({
    url: '/api/chats_count',
    success: function(data) {
        chats_count.innerHTML = '<ion-icon name="chatbubbles"></ion-icon>Chats: ' + data["data"]
    }
    });
}


function LoadChatHeader(){
    if (document.getElementById("chat_id").innerHTML == 0 || document.getElementById("chat_id").innerHTML == ""){
        chat_header.style.visibility = "hidden";
        input_messege_bar.style.visibility = "hidden";
        godown.style.visibility = "hidden";
    }
    else {
        chat_header.style.visibility = "visible";
        input_messege_bar.style.visibility = "visible";
        godown.style.visibility = "visible";
    }
}


function RedirectToUser(a){
        $.ajax({
        url: '/api/find_private_chat/' + a,
        success: function(data) {
            if (data["data"] != 0) {
                OpenChat(data["data"]);
            }
            else {
                $.ajax({
                url: '/api/add_chat_v/private_chat/1/' + a  + '/' + '1' + '/' + document.getElementById("user_id").innerHTML,
                success: function(data) {
                    OpenChat(data["data"]);
                }
                });
            }
        }
        });
}


function AddUserInChat(chat_id, user_id){
    $.ajax({
    url: '/api/user_add_in_chat/' + chat_id + '/' + user_id,
    success: function() {
    }
    });
    setTimeout(() => {
        $.ajax({
        url: '/api/get_settings_add_members_html/' + chat.innerHTML,
        success: function(data) {
            $('#add_member_div').html(data["data"]);
        }
        });

        $.ajax({
        url: '/api/get_settings_members_html/' + chat_id,
        success: function(data) {
            $('#members_div').html(data["data"]);
        }
        });
    }, 10);
}


function DeleteUserFromChat(chat_id, user_id){
    $.ajax({
    url: '/api/delete_member_from_chat/' + chat_id + '/' + user_id,
    success: function() {
    }
    });

    setTimeout(() => {
        $.ajax({
        url: '/api/get_settings_members_html/' + chat_id,
        success: function(data) {
            $('#members_div').html(data["data"]);
        }
        });

        $.ajax({
        url: '/api/get_settings_add_members_html/' + chat.innerHTML,
        success: function(data) {
            $('#add_member_div').html(data["data"]);
        }
        });
    }, 10);
}

function DeleteChat() {
    $.ajax({
    url: '/api/leave_chat/' + chat.innerHTML,
    success: function() {
        chat_settings_bar.classList.remove('active');
        chat.innerHTML = "";
        $('#cont').html("");
        LoadChatHeader();
    }
    });
    setTimeout(() => { updateChats(); }, 10);
}


function sendBackground() {
    let img = bk_img_sel.value;

    let xhr = new XMLHttpRequest();
    let url = "/api/change_bg_img";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
    };
    var data = JSON.stringify({ "img": img});
    xhr.send(data);
}


function ChangeBackground(){
    if (bk_img_sel.value != ""){
        document.getElementById("background").style = ("background-image: url('" + bk_img_sel.value + "');")
        sendBackground();
        document.getElementById("pre_img2").setAttribute('src', document.getElementById("pre_img1").src);
        document.getElementById("pre_img1").setAttribute('src', bk_img_sel.value);
    }
}

function SwitchBackground(){
    buff = document.getElementById("pre_img1").src
    document.getElementById("pre_img1").setAttribute('src', document.getElementById("pre_img2").src);
    document.getElementById("pre_img2").setAttribute('src', buff);
    document.getElementById("background").style = ("background-image: url('" + document.getElementById("pre_img1").src + "');");

    let xhr = new XMLHttpRequest();
    let url = "/api/change_bg_img";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
    };
    var data = JSON.stringify({ "img": document.getElementById("pre_img1").src});
    xhr.send(data);
}

function ChangeChatImg(){
    if (chat_img.value != ""){
        document.getElementById("back_img").style = ("background-image: url('" + chat_img.value + "');")
        document.getElementById("chat_img_set").setAttribute('src', chat_img.value);
    }
}

function ChangeProfileImg(){
    if (profile_img_sel.value != ""){
        document.getElementById("back_profile_img").style = ("background-image: url('" + profile_img_sel.value + "');");
        document.getElementById("profile_img_set").setAttribute('src', profile_img_sel.value);
        sendJSON();
    }
}

function OnOffAddMember() {
    if (add_member_div.classList == "add_member_div active"){
        add_member_div.classList.remove('active');
        members_div.classList.add('active');
    }
    else{
        add_member_div.classList.add('active');
        members_div.classList.remove('active');
    }
}

function OnOffChatImg() {
    if (img_div.classList == "img_div active"){
        img_div.classList.remove('active');
        members_div.classList.add('active');
    }
    else{
        img_div.classList.add('active');
        members_div.classList.remove('active');
        add_member_div.classList.remove('active');
    }
}



function OnOffChatSettings() {
    if (chat_settings_bar.classList == "chat_settings_bar active"){
        chat_settings_bar.classList.remove('active');
    }
    else{
        chat_settings_bar.classList.add('active');
        $.ajax({
        url: 'api/get_settings_header/' + chat.innerHTML,
        success: function(data) {
            $('#settings_header_bar').html(data["data"]);
        }
        });

        $.ajax({
        url: 'api/get_settings_info/' + chat.innerHTML,
        success: function(data) {
            $('#chat_settings_info').html(data["data"]);
        }
        });

        $.ajax({
        url: '/api/get_settings_members_html/' + chat.innerHTML,
        success: function(data) {
            $('#members_div').html(data["data"]);
        }
        });

        $.ajax({
        url: '/api/get_settings_add_members_html/' + chat.innerHTML,
        success: function(data) {
            $('#add_member_div').html(data["data"]);
        }
        });
    }
}

function SetPrivateChats(){
    $.ajax({
        url: 'api/get_private_chats',
        success: function(data) {
            $('#private_chats').html(data["data"]);
        }
    });
}

function ChangeChatHead(a){
    $.ajax({
        url: 'api/get_header/' + a,
        success: function(data) {
            $('#chat_header').html(data["data"]);
        }
    });
}

function OpenChat(a){
    chat_id.innerHTML = a
    $.ajax({
        url: 'api/get_messages/' + a,
        success: function(data) {
            $('#cont').html(data["data"]);
                document.getElementById("cont").style.cssText = `
                scroll-behavior: auto;
                color:aliceblue;
                overflow: scroll;
                width: 100%;
                height: 100%;`;
            document.getElementById("cont").scrollBy(0, document.getElementById("cont").scrollHeight);
        }
    });
    ChangeChatHead(a);
    ProfileOFF();
    chat_settings_bar.classList.remove('active');
    add_member_div.classList.remove('active');
    members_div.classList.add('active');
    img_div.classList.remove('active');
    document.querySelector('#chat_img_sel');
    LoadChatHeader();
}


function ProfileON(){
    messeges.classList.remove('active');
    profile.classList.add('active');
}

function ProfileOFF(){
    messeges.classList.add('active');
    profile.classList.remove('active');
}

function AddChatsON(){
    add_chats.classList.add('active');
    chats.classList.remove('active');
    SetPrivateChats();
}

function ChatsON(){
    chats.classList.add('active');
    add_chats.classList.remove('active');
}

function SettingsON(){
    if (profile.classList == "profile active"){
        ProfileOFF();
    }
    else{
        ProfileON();
        LoadChatsCount();
    }
}

function ChengeChats(){
    if (chats.classList == "chats active"){
        AddChatsON();
    }
    else{
        ChatsON();
    }
}


function sendChatForm() {
    let img = document.querySelector('#chat_img_sel');
    let name = document.querySelector('#chat_title');

    let xhr = new XMLHttpRequest();
    let url = "/api/change_img_chat";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
    };
    var data = JSON.stringify({"img": img.value, "name": name.value, "chat_id": document.getElementById("chat_id").innerHTML});
    xhr.send(data);
    img.value = ""
    OnOffChatSettings();
  }


function sendJSON() {
    let img = profile_img_sel.value;

    let xhr = new XMLHttpRequest();
    let url = "/api/change_img";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
    };
    var data = JSON.stringify({ "img": img});
    xhr.send(data);
}

//function SetImg(){
//    $.ajax({
//        url: 'http://127.0.0.1:8080/api/get_img',
//        success: function(data) {
//            profile_img.src = data['data'];
//        }
//    });
//}

function update(){
    var chat_num = document.getElementById("chat_id").innerHTML;
    $.ajax({
    url: 'api/get_messages/' + chat_num,
    success: function(data) {
        var h = document.getElementById("cont").scrollHeight;
        $('#cont').html(data["data"]);
        if (document.getElementById("cont").scrollHeight != h){
            GoDown();
        }
        }
    });
}


function updateChats(){
    $.ajax({
        url: 'api/user_chats',
        success: function(data) {
            $('#chats').html(data["data"]);
        }
    });
}

//function sendMessege() {
//    let text = document.querySelector('#search');
//    let chat_id = document.getElementById("chat_id").innerHTML;
//    let user_id = document.getElementById("user_id").innerHTML;
//    if (text.value){
//    $.ajax({
//        url: 'http://127.0.0.1:8080/api/send_messages/' + chat_id + '/' + user_id + '/' + text.value,
//        success: function(data) {
//            text.value = ''
//            update();
//        }
//    });
//    }
//}

function sendMessege() {
    let text = document.querySelector('#search').value;
    let chat_id = document.getElementById("chat_id").innerHTML;
    let user_id = document.getElementById("user_id").innerHTML;
    if (text){
        let xhr = new XMLHttpRequest();
        let url = "api/send_messages";
        xhr.open("POST", url, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            document.querySelector('#search').value = '';
        };
        var data = JSON.stringify({'text': text, 'chat_id': chat_id, 'user_id': user_id});
        xhr.send(data);
        document.querySelector('#search').value = '';
        setTimeout(() => { update(); }, 10);
    }
}