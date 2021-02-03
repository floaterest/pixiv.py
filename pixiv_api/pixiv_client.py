import json
import hashlib
from datetime import datetime

from constant import PixivConstant
from pixiv_object.token import Token
from pixiv_api.http_client import HTTPClient

from urllib3.exceptions import HTTPError


class PixivClient(HTTPClient):
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
        res = PixivClient.client.post('https://oauth.secure.pixiv.net/auth/token', data=data, headers=headers)
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
        return PixivClient(PixivClient.get_token(data))

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
        return PixivClient(PixivClient.get_token(data))

    # endregion