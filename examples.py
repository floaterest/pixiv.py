import time
from datetime import datetime

from pixiv_api.pixiv_client import PixivClient
from pixiv_object.illusts_page import Illustration, IllustsPage

from requests.models import Response


def stop_sending_me_email(email: str, password: str):
    """
    Use email(or username) and password to get the refresh token
    login will cause Pixiv to send emails saying 'new login in {country}'
    refresh won't
    :param email:
    :param password:
    :return:
    """
    with PixivClient.login(email, password) as api:
        print(api.token.refresh_token)


def i_have_too_much_bookmarks(refresh_token: str):
    """
    Download all the bookmarks and delete them on Pixiv
    :param refresh_token:
    :return:
    """

    def filename(illust: Illustration, i):
        return f'{illust.user.id}-{illust.id}-{i}'

    def request(res: Response, suc):
        if suc:
            return True
        elif res.status_code == 403:
            print('wait for 5 min')
            time.sleep(300)
            return False

    def callback(page: IllustsPage):
        for illust in page.illusts:
            print(datetime.now().strftime('%H%M%S'), 'download', illust.id)
            client.download_illust(illust, True)
            print(datetime.now().strftime('%H%M%S'), 'deleting')
            client.delete_bookmark(illust.id)
        return True

    with PixivClient.refresh(refresh_token) as client:
        client.filename_formatter = filename
        client.request_handler = request

        client.get_user_bookmarks(callback)


