import pymongo
import logging
from datetime import datetime

# Function for connection with database
def db_connect(dbLink, dbName):
    client = pymongo.MongoClient(dbLink)
    logging.info("Connected to MongoDB...")
    if dbName not in client.database_names():
        logging.info("Creating DataBase...")
        md_db = client[dbName]
    else:
        logging.info("Found Existed DataBase...")
        md_db = client.get_database(dbName)
    return md_db


# Function for checking the status of the fetch_data
def fetch_status(md_db, collectionValidate, date, commodity):
    if collectionValidate not in md_db.list_collection_names():
        fetch_check_obj = md_db[collectionValidate]
    else:
        fetch_check_obj = md_db.get_collection(collectionValidate)

    if len(list(fetch_check_obj.find({"commodity": commodity, "date": date}))) == 0:
        fetch_check_obj.insert_one({"commodity": commodity, 'date': datetime.strptime(date, '%d %b %Y')})
        return False
    else:
        return True


# Function for inserting data inside Database
def add_data_to_db(md_db, collection_name, data):
    if collection_name not in md_db.list_collection_names():
        logging.info("Create New Collection : {}".format(collection_name))
        data_store_obj = md_db[collection_name]
    else:
        data_store_obj = md_db.get_collection(collection_name)
    data_store_obj.insert_many(data);
    return "Done"
