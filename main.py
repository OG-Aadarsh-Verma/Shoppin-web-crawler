from project.core.crawler import Crawler
from project.database.domain_mapper import DomainMapper
import asyncio

def main():
    try:
        DomainMapper().save_domain()
        asyncio.run(Crawler().run_crawler())
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except KeyboardInterrupt:
        Crawler().shutdown()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()