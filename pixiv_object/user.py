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
    # sometimes there's no comment
    comment: str = None

    # endregion

    @staticmethod
    def object_hook(d: dict):
        # if at highest level
        if 'profile_image_urls' in d:
            # there's only one url, so no need for an object inside an object
            d['profile_image_urls'] = d['profile_image_urls']['medium']
        return d
