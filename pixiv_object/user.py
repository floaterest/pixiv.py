from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    account: str
    profile_image_urls: str
    is_followed: bool


def parse_user(d: dict) -> User:
    d['profile_image_urls'] = d['profile_image_urls']['medium']
    return User(**d)
