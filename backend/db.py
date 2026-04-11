from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["phishguard"]

users_collection = db["users"]