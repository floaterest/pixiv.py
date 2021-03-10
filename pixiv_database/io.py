import struct


class BinaryReader:
    def __init__(self, path: str):
        self.file = open(path, 'rb')

    def read_byte(self) -> int:
        return int(self.file.read(1)[0])

    def read_bool(self) -> bool:
        return struct.unpack('?', self.file.read(1))[0]

    def read_int(self) -> int:
        return struct.unpack('i', self.file.read(4))[0]

    def read_ushort(self) -> int:
        return struct.unpack('H', self.file.read(2))[0]

    def read_long_long(self) -> int:
        return struct.unpack('q', self.file.read(8))[0]

    def read_string(self) -> str:
        # region read 7 bit encoded int
        # read out an int32 7 bit at a time
        # the high bit of the byte when on means
        # to continue reading more bytes
        b = self.read_byte()
        count = b & 0x7f
        shift = 0
        while b & 0x80:
            b = self.read_byte()
            shift += 7
            count |= (b & 0x7f) << shift

        # endregion
        return bytes(self.file.read(count)).decode()

    # region context manager

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
    # endregion
