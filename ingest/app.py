from flask import Flask
import uuid

app = Flask(__name__)

# generate a unique number according to RFC 4122
def get_unique_id():
    uid = uuid.uuid1()
    return str(uid)

@app.route("/")
def hello_world():
    uid = get_unique_id()
    return uid
