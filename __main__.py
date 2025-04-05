from project.core.crawler import Crawler
from project.database.domain_mapper import DomainMapper
import asyncio

if __name__ == "__main__":
    try:
        DomainMapper().save_domain()
        asyncio.run(Crawler().run_crawler())
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except KeyboardInterrupt:
        Crawler().shutdown()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
