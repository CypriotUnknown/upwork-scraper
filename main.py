import asyncio
from dotenv import load_dotenv
from scraper import Scraper

if __name__ == "__main__":
    load_dotenv()
    scraper = Scraper()
    asyncio.run(scraper.scrape())
