import asyncio
import aiohttp
import os
from urllib.parse import urlparse

from .cache_manager import CacheManager
from ..logs.logger_config import logger
from .scrapper import Scrapper 
from ..database.db import Database

class Crawler:

    def __init__(self):
        self.db = Database()
        self.cache_manager = CacheManager(self.db)
        self.scrapper = Scrapper()
        self.domain_collection = self.db.get_domain_collection()
        self.domain_count = self.domain_collection.count_documents({})
        self.crawled_domains = set()
        self.running_tasks = []


    async def process_url(self, url, session, queue, domain, rp):
        """
            Checks if th URL is compliant with the robots.txt file.
            Processes the URL to extract product links.
        """        
        if not rp.can_fetch("*",url=urlparse(url).path):
            return
        
        html_content = await self.scrapper.fetch_page(url, session)
        if not html_content:
            logger.warning(f"[CRAWL] Failed to fetch {url} or no content.")
            return

        all_links_on_page = self.scrapper.get_all_links(html_content, domain)
        for link in all_links_on_page:
            if link in queue._queue:
                continue
            if self.cache_manager.is_saved(link):
                continue
            
            if self.scrapper.is_valid_product_url(link, domain):
                self.cache_manager.save_product_url(url=link, domain=domain)
                await queue.put(link)
            elif self.scrapper.is_category(link, domain):
                await queue.put(link)
            elif urlparse(domain).netloc == urlparse(link).netloc:
                await queue.put(link)    


    async def worker(self, queue, session, domain, rp):
        """
            Woker function to process URLs from the queue.
        """
        crawl_delay = rp.crawl_delay("*") or 0
        while True:
            if self.check_shutdown_signal(): # To terminate the worker
                logger.info("[CRAWL] Shutdown signal received. Stopping worker.")
                while not queue.empty():
                    queue.task_done()
                break
            
            try:
                url = await asyncio.wait_for(queue.get(), timeout=1)
            except asyncio.TimeoutError:    
                logger.warning(f"[CRAWL] A worker timed out while waiting.")
                break

            if url is None: # To send a signal to stop the worker
                queue.task_done()
                break

            if not self.cache_manager.is_visited(url):
                try:
                    await self.process_url(url=url, session=session, queue=queue,domain= domain, rp=rp)
                except Exception as e:
                    logger.error(f"[CRAWL] Error processing URL {url}: {e}", exc_info=True)
            
            queue.task_done()        
            await asyncio.sleep(crawl_delay)
            self.cache_manager.cache_status()

    async def crawl_domain(self, domain, num_workers=5):
        """
            Crawls a given domain asynchronously while following 'robots.txt'.
        """
        logger.info(msg=f"[CRAWL] Starting to crawl domain: {domain}")
        queue = asyncio.Queue()
        await queue.put(domain)

        async with aiohttp.ClientSession() as session:
            rp = await self.scrapper.get_robots_txt(domain, session)
            if rp is None:
                logger.warning(f"[CRAWL] robots.txt not found for {domain}. Skipping {domain}.")
                return
            while not queue.empty():
                workers = [
                    asyncio.create_task(self.worker(queue, session, domain, rp))
                    for _ in range(num_workers)
                ]
                
                try:
                    # Wait for the queue to be processed
                    await queue.join()
                except asyncio.CancelledError:
                    logger.info("[CRAWL] Shutdown signal received. Cleaning up workers and queue.")
                finally:
                    # Send exit signals to workers
                    for _ in range(num_workers):
                        await queue.put(None)
                await asyncio.gather(*workers)
        
        logger.info(msg=f"[CRAWL] Finished crawling domain: {domain}")
        

    async def run_crawler(self):
        """
            Function that executes the web crawler.
        """
        domains = []
        for domain in self.domain_collection.find():
            domains.append(domain['url'])
        
        if not domains:
            logger.error("[DB] No domains were found in the database.")
            return
        logger.info(msg="[CRAWL] Web crawler started.")  
        self.running_tasks = [
            asyncio.create_task(self.crawl_domain(domain))
            for domain in domains
        ]
        await asyncio.gather(*self.running_tasks)  
        self.shutdown()
        logger.info(msg="[CRAWL] Web crawler terminated.")

    def shutdown(self):
        """
            Shuts down the crawler.
        """
        logger.info("[CRAWL] Shutting down the crawler...")
        for task in self.running_tasks:
            if not task.done():
                try:
                    logger.info(f"[CRAWL] Cancelling task: {task}")
                    task.cancel()
                except asyncio.CancelledError:
                    pass
        
        try:
            os.remove("shutdown.signal")
        except Exception:
            pass
        self.db.close()
        logger.info("[CRAWL] Crawler shutdown complete.")

    def check_shutdown_signal(self):
        """
            Checks if a shutdown.signal (file) has been received.
        """
        if os.path.exists("shutdown.signal"):
            return True
        return False
