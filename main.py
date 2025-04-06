from project.core.crawler import Crawler
from project.database.domain_mapper import DomainMapper
import asyncio
import os

def main():
    try:
        # Fail-safe in case shutdown.signal was not removed previously.
        os.remove("shutdown.signal")
    except Exception:
        pass

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