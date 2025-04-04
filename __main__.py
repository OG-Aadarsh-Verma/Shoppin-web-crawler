from core.crawler import Crawler
from asyncio import run

if __name__ == "__main__":
    run(Crawler().run_crawler())