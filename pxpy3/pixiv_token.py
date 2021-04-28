from dataclasses import dataclass

from pxpy3.pixiv_object import PixivObject


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


@dataclass
class Token(PixivObject):
    # region field
    access_token: str
    expires_in: int
    token_type: str
    scope: str
    refresh_token: str
    user: User
    # sometimes exists, why?
    device_token: str = None

    # endregion

    @staticmethod
    def object_hook(d: dict) -> dict:
        # if at 'user' level
        if 'profile_image_urls' in d:
            d['profile_image_urls'] = ProfileImageUrls(**d['profile_image_urls'])
        # if at highest level
        elif 'access_token' in d:
            d['user'] = User(**d['user'])
        return d
