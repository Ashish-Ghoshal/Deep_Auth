# usr_db_conf/mongo_setup.py

import pymongo
from auth_logic.usr_constants.db_cfg import DATABASE_NM, MONGO_URL_KEY

class MongoDBConn:
    connection = None

    def __init__(self, db_name=DATABASE_NM) -> None:
        if MongoDBConn.connection is None:
            mongo_url = MONGO_URL_KEY
            MongoDBConn.connection = pymongo.MongoClient(mongo_url)
        self.connection = MongoDBConn.connection
        self.database = self.connection[db_name]

    def get_database(self):
        return self.database
