from utils.db import client, candidates_collection

print("Connected:", client.server_info())      # should not error
print("Count before:", candidates_collection.count_documents({}))
candidates_collection.insert_one({"test": "ok"})
print("Count after:", candidates_collection.count_documents({}))
