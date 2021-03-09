from _io import BufferedReader, BufferedWriter


class PixivObject:
    @staticmethod
    def object_hook(d: dict) -> dict:
        pass

    @staticmethod
    def read(f: BufferedReader) -> object:
        pass

    def write(self, f: BufferedWriter):
        pass
