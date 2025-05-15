# utils/db.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

from dotenv import load_dotenv
load_dotenv()
print("MONGO URI is:", os.getenv("MONGODB_URI"))


client = MongoClient(os.getenv("MONGODB_URI"))  
db = client["user_collection"]
candidates = db["users"]

def save_candidate(data):
    print(data,"saved data function triggerd ")
    email = data.get("email")
    if not email:
        return
    
    # Check if candidate already exists
    existing = candidates.find_one({"email": email})
    if existing:
        print("Candidate with this email already exists. Skipping insert.")
        return
    
    # Insert new candidate
    candidates.insert_one(data)
    print("Candidate inserted.")


def get_candidate_by_email(email):
    doc = candidates.find_one({"email": email}, {"_id": False})
    return doc  