import time
from enum import Enum
from typing import List
from dataclasses import dataclass


# region enums
class Restrict(Enum):
    PUBLIC, MYPIXIV_ONLY, PRIVATE = range(3)


class IllustType(Enum):
    ILLUST, MANGA, UGOIRA = range(3)


# endregion

@dataclass
class Illustration:
    id: int
    updated_on: int
    is_available_online: bool
    title: str
    type: str
    # image_urls:dict (included in 'meta_pages')
    caption: str
    restrict: Restrict

    user: object
    # converted to list[str] instead of list[dict]
    tags: List[str]
    tools: List[str]

    create_date: str
    width: int
    height: int
    sanity_level: bytes
    x_restrict: bool
    series: object

    meta_pages: list
    total_view: int
    total_bookmarks: int
    is_bookmarked: bool
    # is_visible:bool (same functionality as 'restrict == 0')
    is_muted: bool
    total_comments: int


# region decoder
def object_hook(d: dict):
    # if at highest level
    if 'illust' in d:
        d = d['illust']
        # see Illustration dataclass for detail
        d.update({
            'updated_on': int(time.strftime('%Y%m%d')),
            'is_available_online': True
        })
        del d['visible']

        # put meta_single_page to meta_pages
        if d.pop('page_count') == 1:
            d['image_urls']['original'] = d.pop('meta_single_page')['original_image_url']
            d['meta_pages'].append(d['image_urls'])
        else:
            d['meta_pages'] = [page['image_urls'] for page in d['meta_pages']]
        del d['image_urls']

        # convert tags
        tags = []
        for ts in [list(t.values()) for t in d['tags']]:
            tags.extend(ts)
        d['tags'] = tags
    return d

# endregion
