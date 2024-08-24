import re
import asyncio
from typing import Optional
from playwright.async_api import Locator
from models import Article, ArticleField
from .clean_string import clean_string


def get_article_coroutines(article: Locator):
    url_coro = article.get_by_role("link").first.get_attribute("href")
    title_coro = article.get_by_role("link").first.text_content()
    description_coro = article.locator(
        "div[data-test='UpCLineClamp JobDescription']"
    ).first.text_content()

    work_type_coro = article.locator(
        "li[data-test='job-type-label']"
    ).first.text_content()
    experience_coro = article.locator(
        "li[data-test='experience-level']"
    ).first.text_content()
    duration_coro = article.locator(
        "li[data-test='duration-label']"
    ).first.text_content()

    fixed_price = article.locator("li[data-test='is-fixed-price']").first.text_content()

    return (
        url_coro,
        title_coro,
        description_coro,
        work_type_coro,
        experience_coro,
        duration_coro,
        fixed_price,
    )


async def construct_job_embed(article: Locator, base_url: str):

    (url, title, description, work_type, experience, duration, fixed_price) = (
        await asyncio.gather(*get_article_coroutines(article), return_exceptions=True)
    )

    url = f"{base_url}{url}" if isinstance(url, str) else None
    duration = duration if isinstance(duration, str) else None
    if duration is not None:
        duration_regex = r"(?i)Est\.?\s*time:\s*(.*)"
        match = re.search(duration_regex, duration)
        if match:
            duration = match.group(1)

    title = clean_string(title) if isinstance(title, str) else None
    description = clean_string(description) if isinstance(description, str) else None
    work_type = clean_string(work_type) if isinstance(work_type, str) else None

    rate_type: Optional[str] = None
    min_rate: Optional[str] = None
    max_rate: Optional[str] = None

    if work_type is not None:
        work_type_regex = r"(?P<rate_type>[\w\s]+)[:]*\s*(?:(?P<min_rate>\$\d*(?:\.\d{2})?)?\s*-\s*(?P<max_rate>\$\d*(?:\.\d{2})?))?"
        match = re.search(work_type_regex, work_type)
        if match:
            rate_type = match.group("rate_type")
            min_rate = match.group("min_rate")
            max_rate = match.group("max_rate")

    fixed_price = fixed_price if isinstance(fixed_price, str) else None
    if fixed_price is not None:
        fixed_price_regex = r"(?i)Est\.?\s*budget:\s*(.*)"
        match = re.search(fixed_price_regex, fixed_price)
        if match:
            fixed_price = match.group(1)

    experience = clean_string(experience) if isinstance(experience, str) else None

    return Article(
        title=title,
        url=url,
        description=description,
        fields=list(
            filter(
                lambda field: field is not None,
                [
                    (
                        ArticleField(
                            name="Experience:",
                            value=experience,
                            inline=True,
                        )
                        if experience
                        else None
                    ),
                    (
                        ArticleField(name="Rate type:", value=rate_type, inline=True)
                        if rate_type
                        else None
                    ),
                    (
                        (
                            ArticleField(
                                name="Rate:",
                                value=(
                                    f"{min_rate} - {max_rate}"
                                    if fixed_price is None
                                    else fixed_price
                                ),
                                inline=True,
                            )
                            if (min_rate and max_rate) or (fixed_price)
                            else None
                        )
                    ),
                    (
                        ArticleField(name="Duration:", value=duration, inline=True)
                        if duration
                        else None
                    ),
                ],
            )
        ),
    )
