from pymongo import MongoClient
import uuid
import time
import random

MIN_SLEEP = 1
MAX_SLEEP = 10
CHANCE_OF_FAILURE = 10

connection_client = MongoClient("mongodb://mongo:password@localhost", 27017)
mongo_client = connection_client.at_bay_db.scans

def wait():
  time.sleep(random.randrange(MIN_SLEEP, MAX_SLEEP + 1))
  return random.randrange(0, CHANCE_OF_FAILURE) != 0

def perform_scan():
  result = mongo_client.find_one({"status": "Accepted"})
  if result is None:
    return False
  scan_id = result['_id']
  mongo_client.update_one({"_id": scan_id}, {"$set": {"status": "Running"}})
  print("performing scan for %s" % scan_id)
  is_success = wait()
  if is_success:
    mongo_client.update_one({"_id": scan_id}, {"$set": {"status": "Complete"}})
    print("scan success for: %s" % scan_id)
  else:
    mongo_client.update_one({"_id": scan_id}, {"$set": {"status": "Error"}})
    print("scan failure for: %s" % scan_id)
  return True

while True:
  has_value = perform_scan()
  if not has_value:
    time.sleep(1)