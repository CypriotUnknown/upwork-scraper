import asyncio
import random
import os
from playwright.async_api import async_playwright, Playwright, Page
from docker_manager import DockerManager
from utilities import construct_job_embed, publish_to_redis, get_configuration_file


class Scraper:
    pw_server_already_started: bool
    pw_server_name: str
    base_url: str
    pw_server_url: str

    def __init__(self) -> None:
        self.pw_server_url = get_configuration_file()["playwright_server_uri"]
        self.base_url = "https://www.upwork.com"
        self.docker = DockerManager()

    async def get_browser(self, p: Playwright):
        if self.pw_server_url is not None:
            print("connecting...")
            return await p.chromium.connect(self.pw_server_url)
        else:
            print("starting local browser...")
            return await p.chromium.launch(headless=os.getenv("HEADLESS", True))

    async def set_headers(self, page: Page, base_url: str):
        await page.set_extra_http_headers(
            {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
                "Connection": "keep-alive",
                "Origin": "https://www.upwork.com",
                "Referer": f"{base_url}/nx/search/jobs/?q=web%20scraping",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "cross-site",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
            }
        )

    async def simulate_human_behavior(self, page: Page):
        # Add a random delay of 1 to 5 seconds to simulate human behavior
        await asyncio.sleep(random.uniform(1, 5))

        # Scroll the page to load additional content
        await page.evaluate("window.scrollBy(0, window.innerHeight)")

        # Add another random delay of 1 to 5 seconds
        await asyncio.sleep(random.uniform(1, 5))

    async def scrape(self):
        self.docker.start_playwright_browser()

        async with async_playwright() as p:
            jobs: list[dict] = []
            try:
                browser = await self.get_browser(p)
            except Exception as err:
                print("Could not start browser:", err)
                return

            context = await browser.new_context()
            page = await context.new_page()

            await self.set_headers(page, self.base_url)

            await page.goto(f"{self.base_url}/nx/search/jobs/?q=web%20scraping")

            await page.screenshot(path="ss.jpg")

            await self.simulate_human_behavior(page)

            page.set_default_timeout(5 * 1000)

            articles = await page.locator("section[data-test='JobsList'] article").all()

            embeds = await asyncio.gather(
                *(
                    construct_job_embed(article=article, base_url=self.base_url)
                    for article in articles
                )
            )

            for embed in embeds:
                if embed is not None:
                    jobs.append(embed.to_dict())

            publish_to_redis(jobs=jobs)

            await browser.close()

            # print(json.dumps({"jobs": jobs}, indent=4))

            self.docker.stop_playwright_browser()
