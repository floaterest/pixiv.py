from dataclasses import dataclass

from pixiv_object.user import User
from pixiv_object.pixiv_page import PixivPage
from pixiv_object.pixiv_object import PixivObject
from pixiv_object.illustration import Illustration


# region subclasses

@dataclass
class UserPreview(PixivObject):
    # region field
    user: User
    illusts: list[Illustration]
    novels: list  # TODO
    is_muted: bool

    # endregion

    @staticmethod
    def object_hook(d: dict) -> dict:
        # region convert user and illusts
        d['user'] = User(**User.object_hook(d['user']))
        for i, illust in enumerate(d['illusts']):
            d['illusts'][i] = Illustration(**Illustration.object_hook(illust))

        # endregion

        # TODO convert novel
        return d


# endregion

@dataclass
class UsersPage(PixivPage, PixivObject):
    user_previews: list[UserPreview]
    next_url: str

    @staticmethod
    def object_hook(d: dict):
        # if at highest level
        if 'user_previews' in d:
            for i, prev in enumerate(d['user_previews']):
                d['user_previews'][i] = UserPreview(**UserPreview.object_hook(prev))
        return d
