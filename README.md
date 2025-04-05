# Web Crawler for Shoppin Assignment

> Note: The currect code will work. But is still not complete.

This is a web crawler made in Python for the following problem statement:

> **Problem Statement:** Crawler for Discovering Product URLs on E-commerce Websites


## Prerequisites

- Python 3.8 or higher



## Installation

1. Clone the repository locally:
   ```bash
   git clone https://github.com/OG-Aadarsh-Verma/Shoppin-web-crawler.git
   cd Shoppin-web-crawler
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   > Note: I suggest doing creating a new python environment before this step. 

---

## Running the Crawler

1. Prepare a `domains.txt` file in the root directory of the project. Add the domains you want to crawl, one per line. For example:
   ```
   https://example.com
   https://another-example.com
   ```

2. Setup an `.env` file in the root directory of the project along with your MongoDB connection URI and DB_NAME. For example: (Strictly follow the naming convention):
   ```
   MONGO_URI=<Your_Connection_URI>
   MONGO_DB_NAME=<Your_DB_name>
   VISITED_LIMIT=<number_of_sites_to_cache_before_flush> [Optional]
   PRODUCT_LIMIT=<number_of_sites_to_cache_before_flush> [Optional]
   ```

3. Run the crawler:
   ```bash
   python3 __main__.py
   ```