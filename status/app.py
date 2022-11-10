from flask import Flask
from pymongo import MongoClient
import uuid
import os

app = Flask(__name__)

connection_client = MongoClient("mongodb://mongo:password@localhost", int(os.environ['MONGO_PORT']))
mongo_client = connection_client.at_bay_db.scans

# formats a single scan ID for output
def format_one(v):
  return "%s : %s" % (v['_id'], v['status'])

# formats all scans in the system for output
def format_all(vs):
  result = ""
  for v in vs:
    result += format_one(v) + "<br>\r\n"
  return result

# get all scan ids
@app.route("/", methods=['GET'])
def index():
  results = mongo_client.find()
  return format_all(results)

# get a specific scan id
@app.route("/<scan_id>", methods=['GET'])
def single_scan(scan_id):
    result = mongo_client.find_one({"_id": scan_id})
    if result is None:
      return "%s : Not Found <br>\r\n" % scan_id, 404
    else:
      return format_one(result)