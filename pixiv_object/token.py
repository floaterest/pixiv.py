from dataclasses import dataclass

from pixiv_object.pixiv_object import PixivObject


# region other classes
@dataclass
class ProfileImageUrls:
    px_16x16: str
    px_50x50: str
    px_170x170: str


@dataclass
class User:
    profile_image_urls: ProfileImageUrls
    id: int
    name: str
    account: str
    mail_address: str
    is_premium: bool
    x_restrict: int
    is_mail_authorized: bool

# endregion


@dataclass
class Token(PixivObject):
    # region field

    access_token: str
    expires_in: int
    token_type: str
    scope: str
    refresh_token: str
    user: User
    # endregion

    @staticmethod
    def object_hook(d: dict):
        # reaches highest level?
        if 'access_token' in d:
            # convert dicts to their types
            d['user']['profile_image_urls'] = ProfileImageUrls(**d['user']['profile_image_urls'])
            d['user'] = User(**d['user'])
        return d
