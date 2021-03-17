from dataclasses import dataclass

from pixiv_object.pixiv_object import PixivObject
from pixiv_database.io import BinaryReader, BinaryWriter


@dataclass
class MetaPage(PixivObject):
    # region fields
    square_medium: str
    medium: str
    large: str
    original: str

    # endregion

    @staticmethod
    def object_hook(d: dict) -> dict:
        return d

    @staticmethod
    def read(r: BinaryReader):
        return MetaPage(
            square_medium=r.read_string(),
            medium=r.read_string(),
            large=r.read_string(),
            original=r.read_string(),
        )

    def write(self, w: BinaryWriter):
        w.write_string(self.square_medium)
        w.write_string(self.medium)
        w.write_string(self.large)
        w.write_string(self.original)
