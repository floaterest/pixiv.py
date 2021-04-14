import os
import json
import hashlib
from datetime import datetime

from constant import PixivConstant
from pixiv_object.token import Token
from pixiv_object.user_detail import UserDetail
from pixiv_object.illustration import Illustration
from pixiv_api.http_client import HTTPClient

from urllib3.exceptions import HTTPError


class PixivClient(HTTPClient):
    """
    method that returns the filename(str) when downloading an illustration
    e.g.
        def filename_formatter(illust: Illustration, i: int)->str:
            return f'{illust.user.id}-{illust.id}-{i}'
    """
    filename_formatter: staticmethod

    # region constructor
    def __init__(self, token: Token):
        super().__init__()
        self.token = token
        self._client.headers = {
            'User-Agent': 'PixivIOSApp/7.6.2 (iOS 12.2; iPhone9,1)',
            'Accept-Language': 'en-US',
            'App-OS': 'ios',
            'App-OS-Version': '12.2',
            'App-Version': '7.6.2',
            'Referer': 'https://app-api.pixiv.net/',
            'Authorization': f'Bearer {token.access_token}'
        }

    # endregion

    # region GET & POST
    def _get(self, path: str, params: dict, object_hook: staticmethod = None) -> dict:
        """
        GET request to Pixiv
        :param path: relative path to Pixiv's host
        :param params: query dict
        :param object_hook: convert json to dataclass
        """
        return super(PixivClient, self)._get(PixivConstant.HOST + path, params, object_hook)

    def _post(self, path: str, data: dict, object_hook: staticmethod = None) -> dict:
        """
        POST request to Pixiv
        :param path: relative path to Pixiv's host
        :param data: query dict
        :param object_hook: convert json to dataclass
        """
        return super(PixivClient, self)._post(PixivConstant.HOST + path, data, object_hook)

    # endregion

    # region oauth
    @staticmethod
    def _get_token(data: dict) -> Token:
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
        res = PixivClient.client._post('https://oauth.secure.pixiv.net/auth/token', data=data, headers=headers)
        if res.status_code == 200:
            res = json.loads(res.text, object_hook=Token.object_hook)
            # Pixiv still keeps 'response' for backwards compatibility
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
        return PixivClient(PixivClient._get_token(data))

    @staticmethod
    def refresh(refresh_token: str):
        """
        Create client with refresh token
        (usually won't get email saying new login)
        :param refresh_token refresh token from the user's token
        :return: PixivClient
        """
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        return PixivClient(PixivClient._get_token(data))

    # endregion

    # region download
    def download_illust(self, illust: Illustration):
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
            self.download(page.original, path)

    # endregion

    # region requests
    def get_user_detail(self, user_id=None):
        """
        Get user's info by id
        :param user_id: leave empty to use id from token
        :return: UserDetail
        """
        return UserDetail(**self._get('/v1/user/detail', {
            'user_id': user_id or self.token.user.id
        }, UserDetail.object_hook))

    # endregion
