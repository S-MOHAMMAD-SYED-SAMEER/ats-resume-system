import json

def load_users():

    with open("users.json") as f:
        return json.load(f)


def authenticate(username,password):

    users = load_users()

    if username in users and users[username]["password"] == password:

        return True, users[username]["name"], users[username]["role"]

    return False,None,None