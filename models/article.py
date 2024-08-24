from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class ArticleMedia:
    url: Optional[str] = None


@dataclass
class ArticleAuthor:
    name: Optional[str] = None
    icon_url: Optional[str] = None
    url: Optional[str] = None


@dataclass
class ArticleFooter:
    text: Optional[str] = None
    icon_url: Optional[str] = None


@dataclass
class ArticleField:
    name: str
    value: str
    inline: Optional[bool] = None


@dataclass
class Article:
    title: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[str] = None
    image: Optional[ArticleMedia] = None
    author: Optional[ArticleAuthor] = None
    description: Optional[str] = None
    video: Optional[ArticleMedia] = None
    thumbnail: Optional[ArticleMedia] = None
    footer: Optional[ArticleFooter] = None
    fields: Optional[list[ArticleField]] = None

    def to_dict(self):
        return asdict(self)


# @dataclass
# class Job:
#     url: str
#     title: str
#     description: str
#     work_type: str
#     experience: str
#     duration: Optional[str] = None

#     def to_dict(self):
#         return asdict(self)

# (?P<rate_type>\w+):\s*\$(?P<min_rate>\d*(?:\.\d{2})?)?\s*-\s*\$(?P<max_rate>\d*(?:\.\d{2})?)?
