from .db import Database
from ..logs.logger_config import logger

class DomainMapper:
    def __init__(self):
        self.db = Database()
        self.domain_collection = self.db.get_collection('domains')

    def save_domain(self):
        """
        Saves the domains present in 'domains.txt' to the database.
        """
        try:
            with open('.//domains.txt', 'r') as file:
                for domain in file:
                    domain = domain.strip()
                    if not self.domain_collection.find_one({'url': domain}):
                        self.domain_collection.insert_one({'url': domain})
                        logger.info(f"Domain {domain} saved to the database.")
        except FileNotFoundError:
            logger.warning("Skipping mapping domains as 'domains.txt' file was not found in the root directory.", exc_info=True)
        except Exception as e:
            logger.error(f"Error saving domains to the database: {e}", exc_info=True)
        
        self.db.close()