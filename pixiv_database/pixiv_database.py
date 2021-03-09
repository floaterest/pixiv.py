from pixiv_object.illustration import Illustration


class PixivDatabase:
    # region fields
    path: str
    last_modified_date: int
    username: str
    illustrations: list[Illustration]

    # endregion
