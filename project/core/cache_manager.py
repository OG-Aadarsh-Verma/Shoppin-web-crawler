from ..logs.logger_config import logger
from dotenv import load_dotenv
import os

load_dotenv()

class CacheManager:
    VISITED_LIMIT = os.getenv('VISITED_LIMIT', 100)
    PRODUCT_LIMIT = os.getenv('PRODUCT_LIMIT', 1000)

    def __init__(self, db):
        self.db = db
        self.visited_set = set()
        self.product_set = set()
        self.visited_limit = self.VISITED_LIMIT
        self.product_limit = self.PRODUCT_LIMIT

    def cache_status(self):
        """
            Prints the cache status.
        """
        vis_len = len(self.visited_set)
        prod_len = len(self.product_set)
        logger.info(f"[CACHE] Visited URLs: {vis_len}, Product URLs: {prod_len}")
    
    def is_visited(self, url):
        """
            Checks if the URL has been visited recently.
            Returns True if visited, adds to the set and returns False otherwise.
        """
        if url in self.visited_set:
            return True

        if len(self.visited_set) >= self.visited_limit:
            self.flush_visited_urls()

        self.visited_set.add(url)
        return False

    def is_saved(self, url):
        """
            Checks if the URL is already saved in the product cache.
            Returns True if saved, False otherwise.
        """
        return url in self.product_set

    def save_product_url(self, domain, url):
        """
            Saves the product URLs to cache. Flushes to DB when limit is reached.
        """
        self.product_set.add((domain, url))
        if len(self.product_set) >= self.product_limit:
            self.flush_product_urls()

    def flush_visited_urls(self):
        """
            Flushes the cached visited URLs to the database.
        """
        try:
            self.db.insert_many_unique(
                collection=self.db.get_visited_collection(),
                documents=[{'url': url} for url in self.visited_set]
            )
            self.visited_set.clear()
            logger.info("Visited URLs flushed to the database.")
        except Exception as e:
            logger.error(f"[CACHE] Error flushing visited URLs: {e}", exc_info=True)

    def flush_product_urls(self):
        """
            Flushes the cached product URLs to the database.
        """
        try:
            self.db.insert_many_unique(
                collection=self.db.get_product_collection(),
                documents=[{'domain': domain, 'url': url} for (domain, url) in self.product_set]
            )
            self.product_set.clear()
            logger.info("Product URLs flushed to the database.")
        except Exception as e:
            logger.error(f"[CACHE] Error flushing product URLs: {e}", exc_info=True)
        