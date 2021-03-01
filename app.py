import os
import judge0api as api
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)
client = api.Client("http://sntc.iitmandi.ac.in:3000/submissions/")
client.wait = False
# this will be a dictionary of the following pairs :::: {socket_id : [username,room_id]}
USERS = {}
USER_SOCKET_MAPPING = {}  # {username:socketid}


@app.route("/")  # we will make the url extension have the random hex number
def index():
    return render_template('index.html')

# @app.route("/run" , methods = ['POST'])
# def run_code():


@socketio.on('userdata')
def user_data(data):
    # the userdata that will come in will be username and room_id
    if 'username' in data:
        username = data['username']
        room = data['room_id']
        try:
            del USERS[USER_SOCKET_MAPPING[username]]  # try remove the previous
        except:
            print("This is a fresh user")
        finally:
            USER_SOCKET_MAPPING[username] = request.sid
        # new socket assigned to the user
        USERS[request.sid] = [username, room]
        join_room(room)  # the user joins the room
        emit('new user', data, room=room)


@socketio.on('new action')
def new_action(data):
    # find out who sent the data
    room = USERS[request.sid][1]
    emit('new paint', data, room=room)


@socketio.on('clear canvas')
def clear_canvas():
    room = USERS[request.sid][1]
    emit('clear canvas', room=room)


@socketio.on('get users')
def get_users():
    room = USERS[request.sid][1]
    users = []
    for key in USERS:
        if room == USERS[key][1]:
            users.append(USERS[key][0])
    emit('users', users, room=room)


@socketio.on('undo')
def undo():
    room = USERS[request.sid][1]
    emit('undo', room=room)


@socketio.on('leave room')
def exit_room():
    room = USERS[request.sid][1]
    leave_room(room)  # user has now left the room
    emit('user left', room=room)


@socketio.on('new msg')
def new_msg(data):
    room = USERS[request.sid][1]
    # data['username'] is the username of the person who sent the message
    emit('msg', data, room=room)


@socketio.on('submit code')
def submit_code(data):
    # url = "http://sntc.iitmandi.ac.in:3000/submissions/?base64_encoded=false&wait=true"
    # headers = {
    #     "cache-control": "no-cache",
    #     "Content-Type": "application/json"
    # }
    # body = {
    #     "source_code": data['src'],
    #     "language_id": int(data['lang']),
    #     "stdin": data['stdin'],
    #     "cpu_time_limit": 5
    # }
    # print(body)
    # response = requests.post(url, headers=headers, data=body)
    # print(response.content)

    # submission = api.submission.submit(
    #     client, bytes(data['src'], 'utf-8'),
    #     int(data['lang']), stdin=data['stdin'])
    # submission.load(client)
    # print(submission.stdout)
    submission = api.submission.submit(
        client, b"print(f'Hello {input()}')", 71, stdin=b'Judge0', expected_output=b"Hello Judge0")
    submission.load(client)  # Load the status from the server
    print(submission.stdout)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(
        os.environ.get("PORT", 5000)), debug=True)
