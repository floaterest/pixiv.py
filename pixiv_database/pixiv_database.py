from datetime import datetime

from pixiv_database.io import BinaryReader, BinaryWriter
from pixiv_object.illustration import Illustration


class PixivDatabase:
    # region fields
    path: str
    last_modified_date: int
    username: str
    illustrations: list[Illustration]

    # endregion

    def __init__(self, path: str):
        self.path = path
        with BinaryReader(path) as r:
            self.last_modified_date = r.read_int()
            self.username = r.read_string()
            self.illustrations = [Illustration.read(r) for _ in range(r.read_int())]

    def save_as(self, path: str):
        with BinaryWriter(path) as w:
            w.write_int(int(datetime.now().strftime('%Y%m%d')))
            w.write_string(self.username)
            w.write_int(len(self.illustrations))
            for illustration in self.illustrations:
                illustration.write(w)

    def save(self):
        self.save_as(self.path)
