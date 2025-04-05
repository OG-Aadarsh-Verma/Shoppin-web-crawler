from project.core.crawler import Crawler
from project.database.domain_mapper import DomainMapper
import asyncio

if __name__ == "__main__":
    try:
        DomainMapper().save_domain()
        asyncio.run(Crawler().run_crawler())
    except Exception as e:
        Crawler().shutdown()
