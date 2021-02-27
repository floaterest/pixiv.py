import os
import sys
import json
from enum import Enum

import cloudscraper
from requests.models import Response
from urllib3.exceptions import HTTPError


class HTTPMethod(Enum):
    GET = 'GET'
    POST = 'POST'


class HTTPClient:
    progress_callback: staticmethod
    """
    progress_callback:
        method that will be called on a buffer(81920 bytes) written
    e.g.
        def progress_callback(current:int, total:int):
            percent = current * 100 // total
            # current can be greater than total
            print(min(percent, 100),'%')
    """
    request_failed_handler: staticmethod
    """
    request_failed_handler:
        method that will be called when errors happen after an HTTP resquest 
    e.g.
        def request_failed_handler(response:Response)->bool:
            # if forbidden
            if response.status_code == 403:
                print('waiting for 5 minutes')
                time.sleep(300)
                # try again
                return True
            else:
                return False
    """

    client = cloudscraper.create_scraper()

    # region requests
    def ensure_sucess_status_code(self, res: Response) -> bool:
        """
        Check status code and raises error if request not successful
        """
        if 200 <= res.status_code < 300:
            return True
        elif self.request_failed_handler and self.request_failed_handler(res):
            return False
        else:
            raise HTTPError(res.status_code, res.text)

    @staticmethod
    def unescape(text: str) -> str:
        # convert r'\/' or '\\/' to '/'
        return bytes(text, 'utf8').decode()

    def post(self, url: str, data: dict, object_hook: staticmethod = None) -> dict:
        res = self.client.post(url, data=data)
        if self.ensure_sucess_status_code(res):
            return json.loads(self.unescape(res.text), object_hook=object_hook)
        # if request_failed_handler says 'do it again'
        else:
            self.post(url, data, object_hook)

    def get(self, url: str, params: dict = None, object_hook: staticmethod = None) -> dict:
        res = self.client.get(url, params=params)
        self.ensure_sucess_status_code(res)

        if self.ensure_sucess_status_code(res):
            return json.loads(self.unescape(res.text), object_hook=object_hook)
        # if request_failed_handler says 'do it again'
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
