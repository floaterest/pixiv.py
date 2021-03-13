from dataclasses import dataclass

from pixiv_object.pixiv_object import PixivObject
from pixiv_database.io import BinaryReader, BinaryWriter


@dataclass
class User(PixivObject):
    # region fields
    id: int
    name: str
    account: str
    profile_image_urls: str
    # sometimes there's no is_followed or comment (?)
    is_followed: bool = None
    comment: str = None

    # endregion

    @staticmethod
    def object_hook(d: dict) -> dict:
        # if at highest level
        if 'profile_image_urls' in d:
            # there's only one url, so no need for an object inside an object
            d['profile_image_urls'] = d['profile_image_urls']['medium']
        return d

    @staticmethod
    def read(r: BinaryReader):
        return User(
            id=r.read_int(),
            name=r.read_string(),
            account=r.read_string(),
            profile_image_urls=r.read_string(),
            is_followed=r.read_bool()
        )

    def write(self, w: BinaryWriter):
        w.write_int(self.id)
        w.write_string(self.name)
        w.write_string(self.account)
        w.write_string(self.profile_image_urls)
        w.write_bool(self.is_followed)
