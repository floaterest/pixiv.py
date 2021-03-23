import time
from enum import Enum
from dataclasses import dataclass

from pixiv_database.io import BinaryReader, BinaryWriter


# region enum
class Restrict(Enum):
    PUBLIC, MYPIXIV_ONLY, PRIVATE = range(3)


class IllustType(Enum):
    ILLUST, MANGA, UGOIRA = range(3)


# endregion enum

# region interface
class PixivObject:
    def __init__(self):
        if self.__class__ is PixivObject:
            raise RuntimeError('PixivObject must be subclassed')

    @staticmethod
    def object_hook(d: dict) -> dict:
        raise NotImplementedError()

    @staticmethod
    def read(r: BinaryReader): ...

    def write(self, w: BinaryWriter): ...


class PixivPage:
    next_url: str

    def __init__(self):
        if self.__class__ is PixivObject:
            raise RuntimeError('PixivObject must be subclassed')


# endregion interface

# region common
@dataclass
class User(PixivObject):
    # region fields
    id: int
    name: str
    account: str
    profile_image_urls: str
    # sometimes there's no is_followed or comment (?)
    is_followed: bool = None
    comment: str = ''

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


# endregion common

# region illustration
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


@dataclass
class Illustration(PixivObject):
    # region fields
    # https://www.pixiv.net/artworks/{id}
    id: int
    # date of the last sucessful HTTP request (when visible == True)
    updated_on: int
    title: str
    type: IllustType
    # image_urls:dict (included in 'meta_pages')
    caption: str
    restrict: Restrict

    user: User
    # converted to list[str] instead of list[dict]
    tags: list[str]
    tools: list[str]
    # in iso format
    create_date: str
    width: int
    height: int
    # kinda represents how NSFW the illustration is?
    sanity_level: int
    # True if the illustration is r18
    x_restrict: bool
    series: object

    meta_pages: list[MetaPage]
    total_view: int
    total_bookmarks: int
    is_bookmarked: bool
    """
    if not visible and len(meta_pages):
        the illustration was visible before but not now
    """
    visible: bool
    is_muted: bool
    # DNE when gettig user bookmarks(?)
    total_comments: int = 0

    # endregion

    # region implementation
    @staticmethod
    def object_hook(d: dict) -> dict:
        # if at highest level
        if 'illust' in d:
            return d['illust']
        # if at second highest lever
        elif 'title' in d:
            # region convert d to Illustration type

            # see Illustration dataclass for detail
            d |= {
                'updated_on': int(time.strftime('%Y%m%d')),
            }

            # convert enums
            d['type'] = IllustType[str(d['type']).upper()]
            d['restrict'] = Restrict(d['restrict'])

            # parse user
            d['user'] = User(**User.object_hook(d['user']))

            # region put meta_single_page to meta_pages
            if d.pop('page_count') == 1:
                d['image_urls']['original'] = d.pop('meta_single_page')['original_image_url']
                d['meta_pages'].append(MetaPage(**d['image_urls']))
            else:
                del d['meta_single_page']
                d['meta_pages'] = [MetaPage(**page['image_urls']) for page in d['meta_pages']]
            del d['image_urls']
            # endregion

            # region convert tags
            tags = []
            for ts in [list(t.values()) for t in d['tags']]:
                tags.extend([t for t in ts if t])
            d['tags'] = tags

            # endregion

            # endregion

        return d

    @staticmethod
    def read(r: BinaryReader):
        return Illustration(
            id=r.read_int(),
            updated_on=r.read_int(),
            title=r.read_string(),
            type=IllustType(r.read_byte()),
            caption=r.read_string(),
            restrict=Restrict(r.read_byte()),

            user=User.read(r),
            tags=[r.read_string() for _ in range(r.read_int())],
            tools=[r.read_string() for _ in range(r.read_int())],
            create_date=r.read_string(),
            width=r.read_int(),
            height=r.read_int(),
            sanity_level=r.read_byte(),
            x_restrict=r.read_bool(),

            meta_pages=[MetaPage.read(r) for _ in range(r.read_int())],
            total_view=r.read_int(),
            total_bookmarks=r.read_int(),
            is_bookmarked=r.read_bool(),
            visible=r.read_bool(),
            is_muted=r.read_bool(),
            total_comments=r.read_int(),
            series=None
        )

    def write(self, w: BinaryWriter):
        w.write_int(self.id)
        w.write_int(self.updated_on)
        w.write_string(self.title)
        w.write_byte(self.type.value)
        w.write_string(self.caption)
        w.write_byte(self.restrict.value)

        self.user.write(w)
        w.write_int(len(self.tags))
        for tag in self.tags:
            w.write_string(tag)
        w.write_int(len(self.tools))
        for tool in self.tools:
            w.write_string(tool)
        w.write_string(self.create_date)
        w.write_int(self.width)
        w.write_int(self.height)
        w.write_byte(self.sanity_level)
        w.write_bool(self.x_restrict)

        w.write_int(len(self.meta_pages))
        for meta_page in self.meta_pages:
            meta_page.write(w)
        w.write_int(self.total_view)
        w.write_int(self.total_bookmarks)
        w.write_bool(self.is_bookmarked)
        w.write_bool(self.visible)
        w.write_bool(self.is_muted)
        w.write_int(self.total_comments)
    # endregion


@dataclass
class IllustsPage(PixivPage, PixivObject):
    illusts: list[Illustration]
    next_url: str

    @staticmethod
    def object_hook(d: dict) -> dict:
        # if at highest level
        if 'illusts' in d:
            # convert each dict to Illustration
            for i, illust in enumerate(d['illusts']):
                d['illusts'][i] = Illustration(**Illustration.object_hook(illust))
        return d


# endregion illustration

# region user
# region user detail

@dataclass
class Profile:
    # region fields
    webpage: str
    gender: str
    birth: str
    birth_day: str
    birth_year: str
    region: str
    address_id: str
    country_code: str
    job: str
    job_id: int
    total_follow_users: int
    total_mypixiv_users: int
    total_illusts: int
    total_manga: int
    total_novels: int
    total_illust_bookmarks_public: int
    total_illust_series: int
    total_novel_series: int
    background_image_url: str
    twitter_account: str
    twitter_url: str
    pawoo_url: str
    is_premium: bool
    is_using_custom_profile_image: bool

    # endregion


@dataclass
class ProfilePublicity:
    # region fields
    # str: 'public' or 'privte'
    gender: str
    region: str
    birth_day: str
    birth_year: str
    job: str
    # why is just this bool?
    pawoo: bool

    # endregion


@dataclass
class Workspace:
    pc: str
    monitor: str
    tool: str
    scanner: str
    tablet: str
    mouse: str
    printer: str
    desktop: str
    music: str
    desk: str
    chair: str
    comment: str
    workspace_image_url: str


@dataclass
class UserDetail(PixivObject):
    # region fields
    user: User
    profile: Profile
    profile_publicity: ProfilePublicity
    workspace: Workspace

    # endregion

    @staticmethod
    def object_hook(d: dict) -> dict:
        # if at highest level
        if 'user' in d:
            types: list[type] = [User, Profile, ProfilePublicity, Workspace]
            for (k, v), c in zip(d.items(), types):
                d[k] = c(**v)
        return d


# endregion user detail

# region users page

@dataclass
class UserPreview(PixivObject):
    # region field
    user: User
    illusts: list[Illustration]
    novels: list  # TODO
    is_muted: bool

    # endregion

    @staticmethod
    def object_hook(d: dict) -> dict:
        # region convert user and illusts
        d['user'] = User(**User.object_hook(d['user']))
        for i, illust in enumerate(d['illusts']):
            d['illusts'][i] = Illustration(**Illustration.object_hook(illust))

        # endregion

        # TODO convert novel
        return d


@dataclass
class UsersPage(PixivPage, PixivObject):
    user_previews: list[UserPreview]
    next_url: str

    @staticmethod
    def object_hook(d: dict) -> dict:
        # if at highest level
        if 'user_previews' in d:
            for i, prev in enumerate(d['user_previews']):
                d['user_previews'][i] = UserPreview(**UserPreview.object_hook(prev))
        return d

# endregion users page

# endregion user
