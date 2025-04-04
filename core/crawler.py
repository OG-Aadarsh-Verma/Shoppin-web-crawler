import random
import asyncio
import aiohttp
from urllib.parse import urlparse

from core.logger_config import logger
from core.scapper import get_robots_txt, fetch_page, get_all_links, is_valid_product_url, is_category

visited = set()

def is_visited(url):
    """
        Checks if the URL has already been visited.
        Returns True if visited, False otherwise.
    """
    # Turn into DB call after DB setup
    # try:
    #     with open("visited_urls.txt", "r") as visited:
    #         if url in visited:
    #             return True
    #     with open("visited_urls.txt", "a") as visited:
    #         visited.write(url + "\n")
    #         return False
    # except FileNotFoundError as e:
    #     logger.error(msg="Unable to find or open the visited URLs file.", exc_info=True)
    #     return True
    # except Exception as e:
    #     logger.error(msg="An unexpected error occurred while checking visited URLs.", exc_info=True)
    #     return True
    if url in visited:
        return True
    visited.add(url)
    return False

def save_product_url(url):
    """
        Saves the product URL to a file.
    """
    # Turn into DB call after DB setup
    file_path='./data/product_urls.txt'
    try:
        with open(file_path, "r") as product_urls:
            if url in product_urls:
                return
        with open(file_path, "a") as product_urls:
            product_urls.write(url + "\n")
    except FileNotFoundError as e:
        logger.error(msg="Unable to find or open the product URLs file.", exc_info=True)
    except Exception as e:
        logger.error(msg="An unexpected error occurred while saving product URLs.", exc_info=True)

async def process_url(url, session, queue, domain, rp):
    """
        Checks if th URL is compliant with the robots.txt file ans has not been visited.
        Returns a list of urls to be added to the queue.
    """
    if is_visited(url):
        return
    
    if not rp.can_fetch("*",url=urlparse(url).path):
        return
    
    html_content = await fetch_page(url, session)
    if not html_content:
        logger.warning(f"Failed to fetch {url} or no content.")
        return

    all_links_on_page = get_all_links(html_content, domain)
    for link in all_links_on_page:
        if link in queue._queue:
            continue

        if is_valid_product_url(link, domain):
            save_product_url(link)
            await queue.put(link)
        elif is_category(link, domain):
            # print(link)
            await queue.put(link)
        elif urlparse(domain).netloc == urlparse(link).netloc:
            await queue.put(link)

async def worker(queue, session, domain, rp,):
    """
        Woker function to process URLs from the queue.
    """
    crawl_delay = rp.crawl_delay("*") or random.uniform(1, 3)
    # print('worker called')
    # while True:
        
    #     if url is None:
    #         break
    url = await queue.get()
    await process_url(url=url, session=session, queue=queue,domain= domain, rp=rp)
    await asyncio.sleep(crawl_delay)
    queue.task_done()

async def crawl_domain(domain, num_workers=5):
    """
        Crawls a given domain asynchronously while following 'robots.txt'.
        Save a list of product URLs found on the domain.
    """
    logger.info(msg=f"Starting to crawl domain: {domain}")
    queue = asyncio.Queue()
    await queue.put(domain)

    async with aiohttp.ClientSession() as session:
        rp = await get_robots_txt(domain, session)
        if rp is None:
            logger.warning(f"robots.txt not found for {domain}. Skipping the domain.")
            return
        
        while not queue.empty() :
            workers = [
                asyncio.create_task(worker(queue, session, domain, rp))
                for _ in range(num_workers)
            ]
            await asyncio.gather(*workers)
    
    logger.info(msg=f"Finished crawling domain: {domain}")
        

async def run_crawler():
    """
        Function that executes the web crawler.
        Reads the domains to crawl from 'domains.txt' file.
    """

    logger.info(msg="Web crawler started.")
    domains = []
    try:
        # Turn into DB call after DB setup
        with open("./data/domains.txt", "r") as domains_file:
            for domain in domains_file:
                domains.append(domain.strip())
    except FileNotFoundError as e:
        logger.error(msg="Unable to find or open the domains to crawl.", exc_info=True)
        return
    
    tasks = [crawl_domain(domain) for domain in domains]
    await asyncio.gather(*tasks)  

    logger.info(msg="Web crawler terminated.")
