# Pixiv API
## Get Refresh Token
Since logging in with email/username and password will cause pixiv.net to send a email saying:
> [pixiv] 新しいログインがありました (場所: {country}) <br>
> [pixiv] New login to pixiv from {country} <br>

To avoid this, get the refresh_token first:
```py
from pixiv_api.pixiv_client import PixivClient

# will receive email from pixiv.net
with PixivClient.login('email', 'password') as client:
    print(client.token.refresh_token)
```
So for the next time, use refresh token to login:
```py
from pixiv_api.pixiv_client import PixivClient

# will not receive email from pixiv.net
with PixivClient.refresh('refresh token') as client:
    # HTTP resquests
```
[Token dataclass](./pixiv_object/token.py#L29)

## Get user detail
```py
client.get_user_detail(user_id=None) -> UserDetail
```
### Examples
```py
from pixiv_api.pixiv_client import PixivClient

with PixivClient.refresh('refresh token') as client:
    # detail of yourself
    me = client.get_user_detail()
    # detail of another user
    sakimori = client.get_user_detail(211515)
```
[Method definition](./pixiv_api/pixiv_client.py#L138)<br>
[UserDetail dataclass](./pixiv_object/user_detail.py#L82)
