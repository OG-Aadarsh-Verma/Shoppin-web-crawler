# Documentation on Approach

This document explains the whole codebase and the approach of how the crawler handles finding the URLs.

## **Classes**
The codebase is divided into 5 main classes:
- `CacheManager()`
- `Crawler()`
- `Database()`
- `DomainMapper()`
- `Scrapper()`

> **Note**: Any code outside these classes is irrelevant to the logic of the crawler and is just present for alternate uses (such as logging or output formatting, according to the problem statement).

---

## **`Crawler()`**
### **Function List**
- `process_url()`
- `worker()`
- `crawl_domain()`
- `run_crawler()`
- `shutdown()`
- `check_shutdown_signal()`

### **Description**
This class contains the core logic of the crawler.

#### **Logic Flow**
1. Creating an instance of the `Crawler()` class initializes one instance each of:
   - `Scrapper()`: Handles fetching and parsing web pages.
   - `CacheManager()`: Manages caching and deduplication of visited/product URLs.
   - `Database()`: Handles database operations.
2. The `run_crawler()` function is the entry point for the crawler. It:
   - Fetches the list of domains from the database.
   - Creates async tasks for each domain and calls `crawl_domain()` function.
   - `crawl_domain()` function implements `asyncio.Queue()`; therefore, each domain gets its own process queue independent of the other domains.
   - Allows simultaneous calls to multiple domains, decreasing wait time and increasing performance.
3. The `crawl_domain()` function handles a domain by using an `asyncio.Queue()`. It:
    - Initializes and adds the domain to the queue.
    - Establishes a `ClientSession()` and checks for `robots.txt` and creates the robot parser (`rp`).
    - Creates async workers and calls the `worker()` function.
    - Repeats until the queue is empty.
4. The `worker()` function processes URLs from the queue:
    - Ensures compliance with `robots.txt` if the URL can be fetched or not.
    - Checks if the URL was recently visited (in cache).
5. The `process_url()` function uses the `Scrapper()` object:
    - Fetches the page, extracts all `<a>` tags and `<link>` tag links.
    - Checks if any of the links match the patterns [product/category].
    - Pushes valid links back into the queue.
6. The `shutdown()` function ensures a graceful shutdown of the crawler, canceling all tasks and closing the database connection.

---

## **`Scrapper()`**
### **Function List**
- `fetch_page()`
- `get_all_links()`
- `is_valid_product_url()`
- `is_category()`
- `get_robots_txt()`

### **Description**
This class handles all the tasks related to fetching, parsing web pages and validating the patterns.

#### **Function Details**
1. **`fetch_page(url, session)`**:
   - Fetches the HTML content of the given URL using an `aiohttp` session.
   - Returns the HTML content or `None` if the request fails.

2. **`get_all_links(html_content, domain)`**:
   - Extracts all links from the given HTML content.
   - Filters links to ensure they belong to the same domain.

3. **`is_valid_product_url(url, domain)`**:
   - Checks if the given URL matches the criteria for a product page.

4. **`is_category(url, domain)`**:
   - Checks if the given URL matches the criteria for a category page.

5. **`get_robots_txt(domain, session)`**:
   - Fetches and parses the `robots.txt` file for the given domain.
   - Returns a `RobotFileParser` object.

---

## **`CacheManager()`**
### **Function List**
- `is_visited()`
- `is_saved()`
- `save_product_url()`
- `flush_visited_urls()`
- `flush_product_urls()`

### **Description**
This class handles caching and deduplication of visited URLs and product URLs.

#### **Function Details**
1. **`is_visited(url)`**:
   - Checks if the given URL has already been visited.
   - Adds the URL to the visited cache if it hasn't been visited.

2. **`is_saved(url)`**:
   - Checks if the given URL is already saved in the product cache.

3. **`save_product_url(domain, url)`**:
   - Saves the given product URL to the product cache.
   - Flushes the cache to the database when the cache limit is reached.

4. **`flush_visited_urls()`**:
   - Flushes the visited URLs cache to the database.

5. **`flush_product_urls()`**:
   - Flushes the product URLs cache to the database.

---

## **`Database()`**
### **Function List**
- `get_collection()`
- `get_product_collection()`
- `get_visited_collection()`
- `get_domain_collection()`
- `insert_many_unique()`
- `close()`

### **Description**
This class handles all tasks related to the database. Initializing the class opens a connection to the MongoDB client.

#### **Function Details**
1. **`get_collection(name)`**:
   - Returns a MongoDB collection by name.

2. **`get_product_collection()`**:
   - Returns the `product_urls` collection.

3. **`get_visited_collection()`**:
   - Returns the `visited_urls` collection.

4. **`get_domain_collection()`**:
   - Returns the `domains` collection.

5. **`insert_many_unique(collection, documents)`**:
   - Inserts multiple documents into the given collection while ensuring uniqueness.
   - Skips duplicate entries.

6. **`close()`**:
   - Closes the MongoDB connection.

---

## **`DomainMapper()`**
### **Function List**
- `save_domain()`

### **Description**
This class was created with the sole purpose of defining all the domains of websites that should be crawled and pushing them into the database *before* running the crawler.

#### **Function Details**
1. **`save_domain()`**:
   - Reads domains from a `domains.txt` file.
   - Inserts the domains into the `domains` collection in the database.
   - Skips duplicate entries using MongoDB's `ordered=False` option.

---

## **Additional Notes**
- **Logging**:
  - The codebase uses a centralized logging system (`logger`) to log important events, warnings, and errors.
  - Logs are categorized by components (e.g., `[CRAWL]`, `[DB]`, `[MONITOR]`) for better readability.
  - Two types of loggers are used. One logs to the console [For Debugging]. Other logs to a log file [For Maintainence].
