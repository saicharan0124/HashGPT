from pymongo import MongoClient


def init_db():
    # Connect to the MongoDB server (assuming it's running locally on the default port)
    client = MongoClient('localhost', 27017)

    # Check if the "hashGPT" database already exists
    db_names = client.list_database_names()
    if 'hashGPT' not in db_names:
        # Create the "hashGPT" database
        db = client['hashGPT']

        # Add authentication if needed
        # db.command("createUser", "your_username", pwd="your_password", roles=["readWrite"])

        # Create the "doc_collection" collection
        doc_collection = db['doc']

        # Create the "user_collection" collection
        users_collection = db['user']

        # Optionally, you can add initial data or indexes here

        print("Database 'hashGPT' with collections 'doc' and 'user' created successfully.")
        return doc_collection, users_collection
    else:
        print("Database 'hashGPT' already exists. Skipping creation.")
        doc_collection = client['hashGPT']['doc']
        users_collection = client['hashGPT']['user']
        return doc_collection, users_collection
