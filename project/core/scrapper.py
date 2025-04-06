from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import aiohttp
from asyncio import TimeoutError 


from ..logs.logger_config import logger

class Scrapper:
    def __init__(self):
        self.ua = UserAgent()

    async def fetch_page(self, url, session):
        """
            Fetches the content of a webpage.
            Returns the HTML content if successful, None otherwise.
        """
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/'
        }
        try:
            async with session.get(url,headers=headers, timeout=10) as res:
                if res.status == 200:
                    return await res.text()
                else:
                    logger.error(f"[SCRAP] Failed to fetch {url}. Status code: {res.status}")
                    return None
        except aiohttp.ClientError as e:
            logger.error(f"[SCRAP] Error fetching {url}: {e}")
            return None
        except TimeoutError:
            logger.error(f"[SCRAP] Timeout while fetching {url}")
            return None
        except UnicodeDecodeError as ude:
            logger.error(f"[SCRAP] Possibily redundant link. Decode error on {url}.")
        except Exception as e:
            logger.error(f"[SCRAP] Unexpected error while fetching {url}: {e}", exc_info=True)
            return None

    async def get_robots_txt(self, domain, session):
        """
            Fetches the robots.txt file from the given domain.
            Parses it and returns a RobotFileParser object.
            If the robots.txt file is not found, returns None.
        """
        robots_url = urljoin(domain, "robots.txt")
        robot_parser = RobotFileParser()
        robot_parser.set_url(robots_url)
        try:
            async with session.get(robots_url) as response:
                text = await response.text()
                robot_parser.parse(text.splitlines())
        except Exception as e:
            logger.error(f"Failed to read robots.txt from {robots_url}", exc_info=True)
            return None
        return robot_parser

    def get_all_links(self, html_content, base_url):
        """
            Extracts all absolute links from a page's HTML content.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            absolute_url = urljoin(base_url, href)
            links.add(absolute_url)
        for link_tag in soup.find_all('link', href=True):
            href = link_tag['href']
            absolute_url = urljoin(base_url, href)
            links.add(absolute_url)
        return links

    def is_valid_product_url(self, url, domain):
        """
            Determines if a URL is a valid product link based on common patterns.
        """
        parsed_domain_url = urlparse(domain)
        parsed_url = urlparse(url)
        product_patterns = ['/product', '/item', '/p/', '/p-']
        if parsed_domain_url.netloc == parsed_url.netloc:
            for pattern in product_patterns:
                if pattern in parsed_url.path:
                    return True
                    
        return False

    def is_category(self, url, domain):
        """
            Determines if a URL is a category page based on its structure.
        """
        parsed_domain_url = urlparse(domain)
        parsed_url = urlparse(url)
        category_patterns = ['/men', '/women', '/category', '/c/', '/collection']
        if parsed_domain_url.netloc == parsed_url.netloc:
            for pattern in category_patterns:
                if pattern in parsed_url.path:
                    return True
        return False