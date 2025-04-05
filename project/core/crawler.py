import random
import asyncio
import aiohttp
from urllib.parse import urlparse

from ..logs.logger_config import logger
from .scrapper import Scrapper 

from ..database.db import Database

class Crawler:
    VISITED_LIMIT = 100
    PRODUCT_LIMIT = 1000

    def __init__(self):
        self.db = Database()
        self.visited_collection = self.db.get_collection('visited_urls')
        self.product_collection = self.db.get_collection('product_urls')
        self.domain_collection = self.db.get_collection('domains')
        self.scrapper = Scrapper()
        self.running_tasks = []
        self.visited_set = set()
        self.product_set = set()

    def is_visited(self, url):
        """
            Checks if the URL has already been visited.
            Returns True if visited, False otherwise.
        """
        if len(self.visited_set) < self.VISITED_LIMIT:
            if url in self.visited_set:
                return True
            self.visited_set.add(url)
            return False
        if len(self.visited_set) == self.VISITED_LIMIT:
            self.visited_collection.insert_many({'url': val} for val in self.visited_set)
            self.visited_set.add('x')

        if self.visited_collection.find_one({'url': url}):
            return True
        self.visited_collection.insert_one({'url': url})
        return False

    def is_saved(self, url):
        """
            Checks if the URL is already saved in the product collection.
            Returns True if saved, False otherwise.
        """
        if len(self.product_set) < self.PRODUCT_LIMIT:
            if url in self.product_set:
                return True
            self.product_set.add(url)
            return False
        
        return self.product_collection.find_one({'url': url}) is not None
    
    def save_product_url(self, domain, url):
        """
            Saves the product URL to a file.
        """
        if len(self.product_set)<self.PRODUCT_LIMIT:
            self.product_set.add(url)
        if len(self.product_set) == self.PRODUCT_LIMIT:
            self.product_collection.insert_many({'url': val} for val in self.product_set)
            self.product_set.add('x')

        if not self.product_collection.find_one({'domain': domain, 'url': url}):
            self.product_collection.insert_one({'domain': domain, 'url': url})
        

    async def process_url(self, url, session, queue, domain, rp):
        """
            Checks if th URL is compliant with the robots.txt file.
            Processes the URL to extract product links.
        """        
        if not rp.can_fetch("*",url=urlparse(url).path):
            return
        
        html_content = await self.scrapper.fetch_page(url, session)
        if not html_content:
            logger.warning(f"Failed to fetch {url} or no content.")
            return

        all_links_on_page = self.scrapper.get_all_links(html_content, domain)
        for link in all_links_on_page:
            if link in queue._queue:
                continue
            if self.is_saved(link):
                continue
            
            if self.scrapper.is_valid_product_url(link, domain):
                self.save_product_url(url=link, domain=domain)
                await queue.put(link)
            elif self.scrapper.is_category(link, domain):
                await queue.put(link)
            elif urlparse(domain).netloc == urlparse(link).netloc:
                await queue.put(link)
    
    def progress_status(self):
        """
            Periodically prints the progress of the crawler.
        """
        vis_len = len(self.visited_set)
        prod_len = len(self.product_set)
        visited_count = self.visited_collection.count_documents({}) if vis_len == 0 else vis_len  
        product_count = self.product_collection.count_documents({}) if prod_len == 0 else prod_len
        logger.info(f"Visited URLs: {visited_count}, Product URLs: {product_count}")


    async def worker(self, queue, session, domain, rp):
        """
            Woker function to process URLs from the queue.
        """
        crawl_delay = rp.crawl_delay("*") or 0.5
        while True:
            try:
                url = await asyncio.wait_for(queue.get(), timeout=15)
            except asyncio.TimeoutError:    
                logger.warning(f"A worker timed out while waiting.")
                break
            if url is None: # To send a signal to stop the worker
                queue.task_done()
                break

            if not self.is_visited(url):
                try:
                    await self.process_url(url=url, session=session, queue=queue,domain= domain, rp=rp)
                except Exception as e:
                    logger.error(f"Error processing URL {url}: {e}", exc_info=True)
            
            queue.task_done()        
            await asyncio.sleep(crawl_delay)
            self.progress_status()

    async def crawl_domain(self, domain, num_workers=5):
        """
            Crawls a given domain asynchronously while following 'robots.txt'.
            Save a list of product URLs found on the domain.
        """
        logger.info(msg=f"Starting to crawl domain: {domain}")
        queue = asyncio.Queue()
        await queue.put(domain)

        async with aiohttp.ClientSession() as session:
            rp = await self.scrapper.get_robots_txt(domain, session)
            if rp is None:
                logger.warning(f"robots.txt not found for {domain}. Skipping the domain.")
                return
            while not queue.empty():
                workers = [
                    asyncio.create_task(self.worker(queue, session, domain, rp))
                    for _ in range(num_workers)
                ]
                
                await queue.join()
                for _ in range(num_workers):
                    await queue.put(None)
                await asyncio.gather(*workers)
        
        logger.info(msg=f"Finished crawling domain: {domain}")
        

    async def run_crawler(self):
        """
            Function that executes the web crawler.
            Reads the domains to crawl from 'domains.txt' file.
        """
        domains = []
        for domain in self.domain_collection.find():
            domains.append(domain['url'])
        
        if not domains:
            logger.error("No domains were found in the database.")
            return
        logger.info(msg="Web crawler started.")  
        self.running_tasks = [self.crawl_domain(domain) for domain in domains]
        await asyncio.gather(*self.running_tasks)  
        self.db.close()
        logger.info(msg="Web crawler terminated.")

    def shutdown(self):
        """
            Shuts down the crawler.
        """
        logger.info("Shutting down the crawler...")
        for task in self.running_tasks:
            if not task.done():
                task.cancel()
        
        self.db.close()
        logger.info("Crawler shutdown complete.")


