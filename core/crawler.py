import random
import asyncio
import aiohttp
from urllib.parse import urlparse

from core.logger_config import logger
from core.scrapper import Scrapper 

from database.db import Database

class Crawler:
    def __init__(self):
        self.db = Database()
        self.visited_collection = self.db.get_collection('visited_urls')
        self.product_collection = self.db.get_collection('product_urls')
        self.domain_collection = self.db.get_collection('domains')
        self.scrapper = Scrapper()

    def is_visited(self, url):
        """
            Checks if the URL has already been visited.
            Returns True if visited, False otherwise.
        """
        if self.visited_collection.find_one({'url': url}):
            return True
        self.visited_collection.insert_one({'url': url})
        return False

    def save_product_url(self, domain, url):
        """
            Saves the product URL to a file.
        """
        logger.info(f"Saving product URL: {url} for domain: {domain}")
        if not self.product_collection.find_one({'domain': domain, 'url': url}):
            self.product_collection.insert_one({'domain': domain, 'url': url})
        

    async def process_url(self, url, session, queue, domain, rp):
        """
            Checks if th URL is compliant with the robots.txt file ans has not been visited.
            Returns a list of urls to be added to the queue.
        """
        if self.is_visited(url):
            return
        
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

            if self.scrapper.is_valid_product_url(link, domain):
                self.save_product_url(url=link, domain=domain)
                await queue.put(link)
            elif self.scrapper.is_category(link, domain):
                await queue.put(link)
            elif urlparse(domain).netloc == urlparse(link).netloc:
                await queue.put(link)

    async def worker(self, queue, session, domain, rp,):
        """
            Woker function to process URLs from the queue.
        """
        crawl_delay = rp.crawl_delay("*") or random.uniform(1, 3)

        url = await queue.get()
        await self.process_url(url=url, session=session, queue=queue,domain= domain, rp=rp)
        await asyncio.sleep(crawl_delay)
        queue.task_done()

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
        tasks = [self.crawl_domain(domain) for domain in domains]
        await asyncio.gather(*tasks)  

        logger.info(msg="Web crawler terminated.")
