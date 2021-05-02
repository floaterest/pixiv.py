import os
import json
import hashlib
from typing import Callable
from datetime import datetime
from urllib3.exceptions import HTTPError

from pxpy3.constant import PixivConstant
from pxpy3.pixiv_object import PixivObject, \
    Illustration, IllustsPage, \
    UserDetail, UsersPage, \
    Novel, NovelText
from pxpy3.pixiv_token import Token

import cloudscraper
from requests.models import Response


class HTTPClient:
    request_handler: Callable[[Response, bool], bool] = None
    """
    request_handler:
        method that will be called on each request, returns bool
    e.g.
        def request_handler(res: Response, is_sucessful: bool) -> bool:
            if is_sucessful:
                # unescape
                s = bytes(res.text, 'utf8').decode()
                # convert to an object
                o = json.loads(s)
                with open('data.json', 'w+', 'utf8') as f:
                    f.write(json.dumps(o, ensure_ascii=False, indent=4))
                # continue to process
                return True
            # elif forbidden
            elif res.status_code == 403:
                print('waiting for 5 minutes')
                time.sleep(300)
                # request again
                return False
            # raise error
    """
    progress_callback: Callable[[int, int], None] = None
    """
    progress_callback:
        method that will be called on each buffer(81920 bytes) written
    e.g.
        def progress_callback(current:int, total:int):
            percent = current * 100 // total
            # current can be greater than total
            print(min(percent, 100),'%')
    """

    client = cloudscraper.create_scraper()

    # region requests
    def ensure_sucess_status_code(self, res: Response, handle: bool = False) -> bool:
        """
        Check status code and raises error if request not successful
        :returns true: json will load the content, false: requst again
        """
        is_sucessful = res.ok
        if handle and self.request_handler:
            # return callback's decision
            if (r := self.request_handler(res, is_sucessful)) is not None:
                return r
        elif is_sucessful:
            return True

        res.raise_for_status()

    def post(self, url: str, data: dict, object_hook: Callable[[dict], dict] = None):
        res = self.client.post(url, data=data)
        if not self.ensure_sucess_status_code(res):
            self.post(url, data, object_hook)

    def get(self, url: str, params: dict = None, object_hook: Callable[[dict], dict] = None) -> dict:
        res = self.client.get(url, params=params)
        if self.ensure_sucess_status_code(res, True):
            return res.json(object_hook=object_hook)
        # if handler says 'do it again'
        else:
            self.get(url, params, object_hook)

    # endregion

    # region download
    def download(self, url: str, path: str = '', override: bool = False):
        """
        Download an image
        :param url: url of the image, found in meta_pages or profile_image_urls
        :param path: destination filename, will use filename from url if empty
        :param override: will raise error if false and 'filename' exists
        """
        if not override and os.path.exists(path):
            raise FileExistsError

        res = self.client.get(url, stream=True, headers={'Referer': 'https://app-api.pixiv.net/'})

        data = res.raw.data
        total = len(data)
        buffer_size = 81920
        with open(path, 'wb') as f:
            # (i + 1) to iterate through every end position of the data
            # range(... + 1) to include the last part (where the size <= buffer_size) of the data
            for i in [(i + 1) * buffer_size for i in range(total // buffer_size + 1)]:
                f.write(data[i - buffer_size:i])
                if self.progress_callback:
                    # i can be greater than total
                    self.progress_callback(i, total)

    # endregion

    # region context manager

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
    # endregion


class PixivClient(HTTPClient):
    filename_formatter: Callable[[Illustration, int], str] = None
    """
    method that returns the filename(str) when downloading an illustration
    e.g.
        def filename_formatter(illust: Illustration, i: int)->str:
            return f'{illust.user.id}-{illust.id}-{i}'
    """

    # region constructor
    def __init__(self, token: Token):
        self.token = token
        self.client.headers = {
            'User-Agent': 'PixivIOSApp/7.6.2 (iOS 12.2; iPhone9,1)',
            'Accept-Language': 'en-US',
            'App-OS': 'ios',
            'App-OS-Version': '12.2',
            'App-Version': '7.6.2',
            'Referer': 'https://app-api.pixiv.net/',
            'Authorization': f'Bearer {token.access_token}'
        }

    # endregion

    # region GET & POST methods
    def get(self, path: str, params: dict = None, object_hook: Callable[[dict], dict] = None) -> dict:
        """
        GET request to Pixiv
        :param path: relative path to Pixiv's host
        :param params: query dict
        :param object_hook: convert json to dataclass
        """
        return super(PixivClient, self).get(PixivConstant.HOST + path, params, object_hook)

    def post(self, path: str, data: dict, object_hook: Callable[[dict], dict] = None):
        """
        POST request to Pixiv
        :param path: relative path to Pixiv's host
        :param data: query dict
        :param object_hook: convert json to dataclass
        """
        return super(PixivClient, self).post(PixivConstant.HOST + path, data, object_hook)

    def get_page(self, pixiv_object: type(PixivObject), path: str, params: dict, callback: staticmethod):
        """
        Keep requesting until callback returns false or no next_url
        :param pixiv_object: type of the object expected to receive
        :param path: relative path of the api
        :param params: query
        :param callback: staticmethod that takes the page and returns a boolean
        :return: None
        """
        page = pixiv_object(**self.get(path, params, pixiv_object.object_hook))

        while callback(page) is not False and page.next_url:
            # get next page using next_url
            page = pixiv_object(**super(PixivClient, self).get(page.next_url, object_hook=pixiv_object.object_hook))

    # endregion

    # region oauth
    @staticmethod
    def get_token(data: dict) -> Token:
        """
        Get user token with credentials
        :param data email + password or refresh_token
        """
        local = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        data.update({
            'get_secure_url': 1,
            'client_id': PixivConstant.CLIENT_ID,
            'client_secret': PixivConstant.CLIENT_SECRET,
        })
        headers = {
            'User-Agent': 'PixivAndroidApp/5.0.115 (Android 6.0; PixivBot)',
            'X-Client-Time': local,
            'X-Client-Hash': hashlib.md5((local + PixivConstant.HASH_SECRET).encode('utf8')).hexdigest(),
            'Accept-Language': 'en-US',
        }
        res = HTTPClient.client.post('https://oauth.secure.pixiv.net/auth/token', data=data, headers=headers)

        if res.status_code == 200:
            res = json.loads(res.text, object_hook=Token.object_hook)
            del res['response']
            return Token(**res)
        else:
            raise HTTPError(res.status_code, res.text)

    @staticmethod
    def login(email: str, password: str):
        """
        Create client with email(username) and password
        (might get email saying new login from {country})
        :param email: email or username
        :param password: password
        :return PixivClient
        """
        data = {
            'grant_type': 'password',
            'username': email,
            'password': password
        }
        return PixivClient(PixivClient.get_token(data))

    @staticmethod
    def refresh(refresh_token: str):
        """
        Create client with refresh token
        (usually won'refresh_token get email saying new login)
        :param refresh_token refresh token from the user's token
        :return: PixivClient
        """
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        return PixivClient(PixivClient.get_token(data))

    # endregion

    # region download
    def download_illust(self, illust: Illustration, override: bool = False):
        """
        Download every meta page of an illustration
        """
        for i, page in enumerate(illust.meta_pages):
            if self.filename_formatter:
                path = str(self.filename_formatter(illust, i))
                # [-4:] should be the extension of the file
                if not path.endswith(ext := page.original[-4:]):
                    path += ext
            else:
                path = os.path.basename(page.original)
            self.download(page.original, path, override)

    # endregion

    # region requests
    # region GET
    # region user

    def get_user_detail(self, user_id=None) -> UserDetail:
        """
        Get user's info by id
        :param user_id: leave empty to use id from token
        """
        return UserDetail(**self.get('/v1/user/detail', {
            'user_id': user_id or self.token.user.id
        }, UserDetail.object_hook))

    def get_user_illusts(self, callback: staticmethod, user_id=None):
        """
        Get user's illustrations by user id
        :param callback: method to call after each request, takes IllustPage as argument
        :param user_id: leave empty to use id from token
        :return: None
        """
        self.get_page(IllustsPage, '/v1/user/illusts', {
            'user_id': user_id or self.token.user.id
        }, callback)

    def get_user_bookmarks(self, callback: staticmethod, user_id=None, restrict: str = 'public'):
        """
        Get user's illustrations by user id
        :param callback: method to call after each request, takes IllustPage as argument
        :param user_id: leave empty to use id from token
        :param restrict:
        :return: None
        """
        self.get_page(IllustsPage, '/v1/user/bookmarks/illust', {
            'user_id': user_id or self.token.user.id,
            'restrict': restrict
        }, callback)

    def get_user_followings(self, callback: staticmethod, user_id=None, restrict: str = 'public'):
        """
        Get user's following by user id
        :param callback: method to call after each request, takes UsersPage as argument
        :param user_id: leave empty to use id from token
        :param restrict:
        :return: None
        """
        self.get_page(UsersPage, '/v1/user/following', {
            'user_id': user_id or self.token.user.id,
            'restrict': restrict
        }, callback)

    # endregion

    # region illust
    def get_illust_detail(self, illust_id: int):
        """Get illust's info by id"""
        return Illustration(**self.get('/v1/illust/detail', {
            'illust_id': illust_id
        }, Illustration.object_hook))

    # endregion

    # region novel
    def get_novel_detail(self, novel_id: int):
        """Get novel's info by id"""
        return Novel(**self.get('/v2/novel/detail', {
            'novel_id': novel_id
        }, Novel.object_hook))

    def get_novel_text(self, novel_id: int):
        """Get novel's text by id"""
        return NovelText(**self.get('/v1/novel/text', {
            'novel_id': novel_id
        }, NovelText.object_hook))

    # endregion novel

    # endregion

    # region POST
    def add_bookmark(self, illust_id: int, restrict: str = 'public'):
        self.post('/v2/illust/bookmark/add', {
            'illust_id': illust_id,
            'restrict': restrict
        })

    def delete_bookmark(self, illust_id: int, restrict: str = 'public'):
        self.post('/v1/illust/bookmark/delete', {
            'illust_id': illust_id,
            'restrict': restrict
        })
    # endregion
    # endregion
