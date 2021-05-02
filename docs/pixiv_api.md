# Pixiv API ([source code](../pxpy3/pixiv_api.py))

tl;dr see [examples](pixiv_api_examples.md)

- [Authentication](#authentication)
    - [Login](#login)
    - [Refresh](#refresh)
- [User](#user)
    - [Get User Detail](#get-user-detail)
    - [Get User Illustrations](#get-user-illustrations)
    - [Get User Bookmarks](#get-user-bookmarks)
    - [Get User Followings](#get-user-followings)
- [Illustration](#illustration)
    - [Get Illustration Detail](#get-illustration-detail)
- [Bookmark](#bookmark)
    - [Add Bookmark](#add-bookmark)
    - [Delete Bookmark](#delete-bookmark)
- [Download](#download)
    - [Custom Filenames](#custom-filenames)

## Authentication

Get a user token and create a client for future HTTP requests <br>

### Login

([source code](../pxpy3/pixiv_api.py#L213))

Example:

```py
from pxpy3.pixiv_api import PixivClient

# will receive email
with PixivClient.login('email', 'password') as client:
    print(client.token.refresh_token)
```

- Caution: Loggin in with email and password will cause Pixiv to send an email saying:
  > [pixiv] 新しいログインがありました (場所: {country}) <br>
  [pixiv] New login to pixiv from {country} <br>
- To avoid this, simply login with refresh token obtained from `client.token.refresh_token`

### Refresh

([source code](../pxpy3/pixiv_api.py#L229))

Example:

```py
from pxpy3.pixiv_api import PixivClient

# will not receive email
with PixivClient.refresh('refresh token') as client:
    # HTTP requests
    pass
```

## User

Send GET requests to `/v1/user/*`

- Methods that take the `callback` argument will keep executing `callback(page)` until reach the end or rate limit<br>
  In order to deal with rate limit, set the `request_handler` field:
    ```py
    import time
    
    from requests.models import Response
    
    from pxpy3.pixiv_api import PixivClient
    
    
    def request(response: Response, is_successful: bool) -> bool:
        if is_successful:
            return True
        elif response.status_code == 403:  # forbidden
            print('Calm down for 5 minutes')
            time.sleep(300)
            # send the request again
            return False
        # will raise error
    
    
    with PixivClient.refresh('refresh token') as client:
        client.request_handler = request
        # HTTP requests
    ```

### Get User Detail

([source code](../pxpy3/pixiv_api.py#L265))

Example:

```py
from pxpy3.pixiv_api import PixivClient

with PixivClient.refresh('refresh token') as client:
    # get detail of myself
    myself = client.get_user_detail()
    # get detail of other users
    pixiv_official = client.get_user_detail(11)
```

### Get User Illustrations

([source code](../pxpy3/pixiv_api.py#L274))

Example:

```py
from pxpy3.pixiv_api import PixivClient, IllustsPage


def callback(page: IllustsPage):
    """
    Print every illustration ID in a page
    """
    for illust in page.illusts:
        print(illust.id)


with PixivClient.refresh('refresh token') as client:
    # will call `callback` repeatedly until the end or rate limit
    # get illusts from myself
    client.get_user_illusts(callback)
    # get illusts from user 11 (Pixiv Official)
    client.get_user_illusts(callback, 11)
```

- To avoid rate limit, see under [##User](#user)

### Get User Bookmarks

([source code](../pxpy3/pixiv_api.py#L285))

Example:

```py
from pxpy3.pixiv_api import PixivClient, IllustsPage


def callback(page: IllustsPage):
    """
    Print the url for every illustration in a page
    """
    for illust in page.illusts:
        print(f'https://www.pixiv.net/artworks/{illust.id}')


with PixivClient.refresh('refresh token') as client:
    # this will call `callback` repeatedly until the end or rate limit
    # get my public bookmarks
    client.get_user_bookmarks(callback)
    # get my private bookmarks
    client.get_user_bookmarks(callback, restrict='private')
```

- To avoid rate limit, see under [##User](#user)

### Get User Followings

([source code](../pxpy3/pixiv_api.py#L298))

Example:

```py
from pxpy3.pixiv_api import PixivClient, UsersPage


def callback(page: UsersPage):
    """
    Print the url for every user in a page
    """
    for preview in page.user_previews:
        print(f'https://www.pixiv.net/user/{preview.user.id}')


with PixivClient.refresh('refresh token') as client:
    # this will call `callback` repeatedly until the end or rate limit
    # get my public followings
    client.get_user_followings(callback)
    # get my private followings
    client.get_user_followings(callback, restrict='private')
```

- To avoid rate limit, see under [##User](#user)

## Illustration

Send GET requests to `/v1/illust/*`

### Get Illustration Detail

([source code](../pxpy3/pixiv_api.py#L314))

Example:

```py
from pxpy3.pixiv_api import PixivClient

with PixivClient.refresh('refresh token') as client:
    # Pixiv 1 year anniversary
    pixiv = client.get_illust_detail(1580459)
```

## Bookmark

Send POST requests to `/v2/illust/bookmark/*`

### Add Bookmark

([source code](../pxpy3/pixiv_api.py#L340))

Example:

```py
from pxpy3.pixiv_api import PixivClient

with PixivClient.refresh('refresh token') as client:
    # add a private bookmark
    client.add_bookmark(1580459, 'private')
```

### Delete Bookmark

([source code](../pxpy3/pixiv_api.py#L346))

Example:

```py
from pxpy3.pixiv_api import PixivClient

with PixivClient.refresh('refresh token') as client:
    # delete a public bookmark
    client.delete_bookmark(1580459)
```

## Download

### Custom Filenames

Set the `file_formatter` field in `PixivClient`<br>
Example (Download all public bookmarks):

```py
from pxpy3.pixiv_api import IllustsPage, Illustration, PixivClient


def formatter(illust: Illustration, index: int) -> str:
    # file extension is optional
    return f'{illust.user.id}-{illust.id}-{index}'


def callback(page: IllustsPage):
    for illust in page.illusts:
        client.download_illust(illust)


with PixivClient.refresh('refresh token') as client:
    client.filename_formatter = formatter
    # download every public bookmark
    client.get_user_bookmarks(callback)
  ```