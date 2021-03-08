import os

import cloudscraper
from requests.models import Response


class HTTPClient:
    request_handler: staticmethod = None
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
    progress_callback: staticmethod = None
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

    def post(self, url: str, data: dict, object_hook: staticmethod = None):
        res = self.client.post(url, data=data)
        if not self.ensure_sucess_status_code(res):
            self.post(url, data, object_hook)

    def get(self, url: str, params: dict = None, object_hook: staticmethod = None) -> dict:
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
