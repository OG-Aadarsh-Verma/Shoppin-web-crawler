import random
import asyncio
import aiohttp
from urllib.parse import urlparse

from logger_config import logger
from scapper import get_robots_txt, fetch_page, get_all_links, is_valid_product_url, is_category




async def crawl_domain(domain):
    """
        Crawls a given domain asynchronously while following 'robots.txt'.
        Return a list of product URLs found on the domain.
    """
    visited = set()
    product_url = set()
    queue = [domain]

    async with aiohttp.ClientSession() as session:
        rp = get_robots_txt(domain, session)
        if rp is None:
            logger.warning(f"robots.txt not found for {domain}. Skipping the domain.")
            return []
        
        crawl_delay = rp.crawl_delay("*") or random.uniform(1, 3)
        while queue:
            current_url = queue.pop(0)
            if current_url in visited:
                continue
            visited.add(current_url)

            if not rp.can_fetch(current_url):
                continue

            html_content = fetch_page(current_url)
            if not html_content:
                continue

            all_links_on_page = get_all_links(html_content, domain)
            for link in all_links_on_page:
                if is_valid_product_url(link, domain):
                    if link not in visited:
                        product_url.add(link)
                        queue.add(link)
                elif is_category(link, domain):
                    if link not in visited:
                        queue.append(link)
                elif urlparse(domain).netloc == urlparse(link).netloc and link not in visited:
                    queue.add(link)
                
            await(asyncio.sleep(crawl_delay))
    return product_url
                    



async def run_crawler():
    """
        Function that executes the web crawler.
        Reads the domains to crawl from 'domains.txt' file.
        Writes the crawled product URLs to 'product_urls.txt'.
    """

    logger.info(msg="Web crawler started.")
    try:
        domains_file = open("./domains.txt", "r")
        domains = []
        for domain in domains_file:
            domains.append(domain.strip())
    except FileNotFoundError as e:
        logger.error(msg="Unable to find or open the domains to crawl.", exc_info=True)
        return
    finally:
        domains_file.close()
    
    tasks = []
    for domain in domains:
        logger.info(msg=f"Starting to crawl domain: {domain}")
        tasks.append(await crawl_domain(domain))
        logger.info(msg=f"Finished crawling domain: {domain}")
    
    results = await asyncio.gather(*tasks)

    logger.info(msg="Web crawler terminated.")
