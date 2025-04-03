from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
import aiohttp

from logger_config import logger

async def fetch_page(url, session):
    """
        Fetches the content of a webpage.
        Returns the HTML content if successful, None otherwise.
    """
    try:
        async with session.get(url, timeout=10) as res:
            if res.status_code == 200:
                return await res.text
            else:
                logger.error(f"Failed to fetch {url}. Status code: {res.status_code}")
                return None
    except aiohttp.ClientError as e:
        logger.error(f"Error fetching {url}: {e}", exc_info=True)
        return None

async def get_robots_txt(domain, session):
    """
        Fetches the robots.txt file from the given domain.
        Parses it and returns a RobotFileParser object.
        If the robots.txt file is not found, returns None.
    """
    robots_url = urljoin(domain, "robots.txt")
    robot_parser = RobotFileParser()
    robot_parser.set_url()
    try:
        async with session.get(robots_url) as response:
            text = await response.text()
            robot_parser.parse(text.splitlines())
    except Exception as e:
        logger.error(f"Failed to read robots.txt from {robots_url}", exc_info=True)
        return None
    return robot_parser

def get_all_links(html_content, base_url):
    """
        Extracts all absolute links from a page's HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        absolute_url = urljoin(base_url, href)
        links.add(absolute_url)
    return links

def is_valid_product_url(url, domain):
    """
        Determines if a URL is a valid product link based on common patterns.
    """
    parsed_domain_url = urlparse(domain)
    parsed_url = urlparse(url)
    product_patterns = ['/product', '/item', '/p/']
    if parsed_domain_url.netloc == parsed_url.netloc:
        for pattern in product_patterns:
            if pattern in parsed_url.path:
                return True
                
    return False

def is_category(url, domain):
    """
        Determines if a URL is a category page based on its structure.
    """
    parsed_domain_url = urlparse(domain)
    parsed_url = urlparse(url)
    category_patterns = ['/category', '/cat', '/men', '/women']
    if parsed_domain_url.netloc == parsed_url.netloc:
        for pattern in category_patterns:
            if pattern in parsed_url.path:
                return True
    return False