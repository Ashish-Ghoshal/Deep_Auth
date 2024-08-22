# usr_db_conf/mongo_setup.py

import pymongo
from auth_logic.usr_constants.db_cfg import DB_NAME_NEW, DB_URL_NEW

class MongoDBConn:
    connection = None

    def __init__(self, db_name=DB_NAME_NEW) -> None:
        if MongoDBConn.connection is None:
            mongo_url = DB_URL_NEW
            MongoDBConn.connection = pymongo.MongoClient(mongo_url)
        self.connection = MongoDBConn.connection
        self.database = self.connection[db_name]

    def get_database(self):
        return self.database
