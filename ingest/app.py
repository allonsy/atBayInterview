from flask import Flask
from pymongo import MongoClient
import uuid
import os

app = Flask(__name__)

connection_client = MongoClient("mongodb://mongo:password@localhost", int(os.environ['MONGO_PORT']))
mongo_client = connection_client.at_bay_db.scans

# generate a unique number according to RFC 4122
def get_unique_id():
  uid = uuid.uuid1()
  return str(uid)

# inserts a uid into the mongo db
def insert_scan_request(uid):
  scan_obj = { "_id": uid, "status": "Accepted" }
  val = mongo_client.insert_one(scan_obj)

@app.route("/")
def index():
  uid = get_unique_id()
  insert_scan_request(uid)
  print("Queued scan request with id %s" % uid)
  return uid
