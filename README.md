# Web Crawler for Shoppin Assignment

This is a web crawler made in Python for the following problem statement:

**Problem Statement:** Crawler for Discovering Product URLs on E-commerce Websites

> Note: Please find the complete documentation of this code inside `Documentation.md`
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
   > Note: I suggest creating a new python environment before this step. 

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
   python3 main.py
   ```

4. Stop the crawler after some time:
   >Note: Run this command in a new terminal.
   ```bash
   python3 project/core/shutdown.py
   ```

5. Write the found urls to a file:
   ```bash
   python3 db_to_file_mapper.py
   ```

> **Note**: All the logs of for the crawler can be found at `project/logs/crawler.log` 