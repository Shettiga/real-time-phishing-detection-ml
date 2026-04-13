from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Create database
db = client["phishguard_db"]

# Collections
users_collection = db["users"]
history_collection = db["history"]