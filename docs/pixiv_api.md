# Pixiv API

## Login

Get a user token and create a client for future HTTP requests <br>

### Login with Email and Password

```py
from pxvpy3.pixiv_api import PixivClient

# will receive email
with PixivClient.login('email', 'password') as client:
    print(client.token.refresh_token)
```

- Caution: Loggin in with email and password will cause Pixiv to send an email saying:
  > [pixiv] 新しいログインがありました (場所: {country}) <br>
  [pixiv] New login to pixiv from {country} <br>
- To avoid this, simply login with refresh token obtained from `client.token.refresh_token`

### Login with Refresh Token

```py
from pxvpy3.pixiv_api import PixivClient

# will not receive email
with PixivClient.refresh('refresh token') as client:
    pass
```

## User

Send GET requests at `/v1/user/*`

### User Detail

```py
def get_user_detail(self, user_id=None) -> UserDetail:
```

```py
from pxvpy3.pixiv_api import PixivClient

with PixivClient.refresh('refresh token') as client:
    # get detail of myself
    myself = client.get_user_detail()
    # get detail of other users
    sakimori = client.get_user_detail(211515)
```