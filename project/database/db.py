from pymongo import MongoClient
from dotenv import load_dotenv
import os

from ..logs.logger_config import logger

load_dotenv()

class Database:
    uri = os.getenv('MONGO_URI')
    db_name = os.getenv('MONGO_DB_NAME')

    if not uri or not db_name:
        logger.error("Missing MongoDB URI or database name in environment variables.")
    def __init__(self):
        logger.info("Connecting to MongoDB...")
        self.client = MongoClient(self.uri) 
        logger.info("Connected to MongoDB.")
        self.db = self.client[self.db_name]

    def get_collection(self, collection_name: str):
        try:
            return self.db[collection_name]
        except Exception as e:
            logger.error(f"Error accessing collection {collection_name}: {e}", exc_info=True)

    def close(self):
        self.client.close()
        logger.info("Closed MongoDB connection.")