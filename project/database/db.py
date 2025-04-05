from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv
import os

from ..logs.logger_config import logger

load_dotenv()

class Database:
    uri = os.getenv('MONGO_URI')
    db_name = os.getenv('MONGO_DB_NAME')
    
    def __init__(self):
        if not self.uri or not self.db_name:
            raise ValueError("Missing MongoDB URI or database name in environment variables.")
        
        logger.info("Connecting to MongoDB...")
        try:
            self.client = MongoClient(self.uri) 
            logger.info("Connected to MongoDB.")
            self.db = self.client[self.db_name]
        except Exception as e:
            logger.error(f"[DB] Error connecting to MongoDB: {e}")
            raise e

    def get_collection(self, collection_name: str):
        try:
            return self.db[collection_name]
        except Exception as e:
            logger.error(f"[DB] Error accessing collection {collection_name}: {e}", exc_info=True)

    def get_product_collection(self):
        """
            Returns the product collection.
        """
        product_collection = self.get_collection('product_urls')
        product_collection.create_index('url', unique=True)
        return product_collection
    
    def get_visited_collection(self):
        """
            Returns the visited collection.
        """
        visited_collection = self.get_collection('visited_urls')
        visited_collection.create_index('url', unique=True)
        return visited_collection
    
    def get_domain_collection(self):
        """
            Returns the domain collection.
        """
        domain_collection = self.get_collection('domains')
        domain_collection.create_index('url', unique=True)
        return domain_collection
    
    def insert_many_unique(self, collection, documents, unique_key='url'):
        """
            Inserts documents into the collection, skips duplicates.
        """
        if not documents:
            logger.warning("No documents to insert in DB.")
            return
        
        try:
            collection.insert_many(documents, ordered=False)
        except BulkWriteError as bwe:
            inserted = bwe.details.get('nInserted', 0)
            logger.error(f"[DB] Inserted {inserted} documents, skipped duplicates.")
        except Exception as e:
            logger.error(f"[DB] Error inserting documents: {e}", exc_info=True)

    def close(self):
        self.client.close()
        logger.info("Closed MongoDB connection.")