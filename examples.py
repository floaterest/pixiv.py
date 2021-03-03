from pixiv_api.pixiv_client import PixivClient


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
