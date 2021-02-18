from dataclasses import dataclass

from pixiv_object.pixiv_object import PixivObject
from pixiv_object.pixiv_page import PixivPage
from pixiv_object.illustration import Illustration


@dataclass
class IllustsPage(PixivPage, PixivObject):
    illusts: list[Illustration]
    next_url: str

    @staticmethod
    def object_hook(d: dict):
        # if at highest level
        if 'illusts' in d:
            # convert each dict to Illustration
            for i, illust in enumerate(d['illusts']):
                d['illusts'][i] = Illustration(**Illustration.object_hook(illust))
        return d
