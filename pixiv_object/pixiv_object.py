from pixiv_database.io import BinaryReader, BinaryWriter


class PixivObject:
    def __init__(self):
        pass

    @staticmethod
    def object_hook(d: dict) -> dict:
        pass

    @staticmethod
    def read(r: BinaryReader):
        pass

    def write(self, w: BinaryWriter):
        pass
