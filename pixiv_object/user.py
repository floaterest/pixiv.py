from dataclasses import dataclass

from pixiv_object.pixiv_object import PixivObject


@dataclass
class User(PixivObject):
    # region fields
    id: int
    name: str
    account: str
    profile_image_urls: str
    is_followed: bool
    comment: str = ''

    # endregion

    @staticmethod
    def object_hook(d: dict):
        d['profile_image_urls'] = d['profile_image_urls']['medium']
        return d
