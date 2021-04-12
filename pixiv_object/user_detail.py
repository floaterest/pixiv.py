from enum import Enum
from dataclasses import dataclass

from pixiv_object.pixiv_user import User
from pixiv_object.pixiv_object import PixivObject


# region enums
class Publicity(Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'


# endregion

# region other classes
@dataclass
class Profile:
    # region fields
    webpage: str
    gender: str
    birth: str
    birth_day: str
    birth_year: str
    region: str
    address_id: str
    country_code: str
    job: str
    job_id: int
    total_follow_users: int
    total_mypixiv_users: int
    total_illusts: int
    total_manga: int
    total_novels: int
    total_illust_bookmarks_public: int
    total_illust_series: int
    total_novel_series: int
    background_image_url: str
    twitter_account: str
    twitter_url: str
    pawoo_url: str
    is_premium: bool
    is_using_custom_profile_image: bool

    # endregion


@dataclass
class ProfilePublicity(PixivObject):
    # region fields
    gender: Publicity
    region: Publicity
    birth_day: Publicity
    birth_year: Publicity
    job: Publicity
    # why is just this bool?
    pawoo: bool

    # endregion

    @staticmethod
    def object_hook(d: dict):
        for k, v in d.items():
            if isinstance(v, str):
                d[k] = Publicity(v)
        return d


@dataclass
class Workspace:
    pc: str
    monitor: str
    tool: str
    scanner: str
    tablet: str
    mouse: str
    printer: str
    desktop: str
    music: str
    desk: str
    chair: str
    comment: str
    workspace_image_url: str


# endregion


@dataclass
class UserDetail(PixivObject):
    # region fields
    user: User
    profile: Profile
    profile_publicity: ProfilePublicity
    workspace: Workspace

    # endregion

    @staticmethod
    def object_hook(d: dict):
        # if at highest level
        if 'user' in d:
            d['user'] = User(**User.object_hook(d['user']))
            d['profile'] = Profile(**d['profile'])
            d['profile_publicity'] = ProfilePublicity(**ProfilePublicity.object_hook(d['profile_publicity']))
            d['workspace'] = Workspace(**d['workspace'])
        return d
