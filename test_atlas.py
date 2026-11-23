
import os
from pymongo import MongoClient

uri = os.getenv("MONGODB_URI")

if not uri:
    raise RuntimeError("MONGODB_URI environment variable is missing")

try:
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=15000
    )

    result = client.admin.command("ping")

    print("Atlas connection successful!")
    print(result)

    print("Databases:", client.list_database_names())

except Exception as e:
    print("Atlas connection failed:")
    print(type(e).__name__)
    print(str(e))

finally:
    if "client" in locals():
        client.close()
