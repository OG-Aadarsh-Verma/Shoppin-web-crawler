from .db import Database
from ..logs.logger_config import logger
from pymongo.errors import BulkWriteError

class DomainMapper:
    def __init__(self):
        self.db = Database()
        self.domain_collection = self.db.get_domain_collection()

    def save_domain(self):
        """
            Saves the domains present in 'domains.txt' to the database.
        """
        try:
            with open('./domains.txt', 'r') as file:
                domains = []
                for domain in file:
                    domains.append({'url':domain.strip()})
                
                self.domain_collection.insert_many(domains, ordered=False)
                logger.info(f"[DB] Domain {domain} saved to the database.")
        except FileNotFoundError:
            logger.warning("[DB] Skipping mapping domains as 'domains.txt' file was not found in the root directory.", exc_info=True)
        except BulkWriteError as bwe:
            inserted = bwe.details.get('nInserted', 0)
            logger.info(f"[DB] Inserted {inserted} domains. Skipping duplicates.")
        except Exception as e:
            logger.error(f"[DB] Error saving domains to the database: {e}", exc_info=True)
        
        self.db.close()