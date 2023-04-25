from fastapi import FastAPI
from pymongo import MongoClient
from bson import json_util
import json

mongo_url = "mongodb+srv://asdf:bAnKMw1ry8RzwaqQ@grants.7itdw0x.mongodb.net/test"
client = MongoClient(mongo_url)
db = client['first']
collection = db.get_collection("grants")
app = FastAPI()

@app.post("/findGrants")
async def findGrants(body: dict):
    allGrants = []
    for i in collection.find({}):
        allGrants.append(i)
    response = json.loads(json_util.dumps(allGrants))
    return {"grants": response}
