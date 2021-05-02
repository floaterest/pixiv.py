# Pixiv API Examples

- [Download and Delete All Public Bookmarks](#download-and-delete-all-public-bookmarks)

## Download and Delete All Public Bookmarks

```py
import os

from pxpy3.pixiv_api import PixivClient, IllustsPage, Illustration


def formatter(illust: Illustration, i: int) -> str:
    if not os.path.exists(str(illust.user.id)):
        os.mkdir(str(illust.user.id))
    return f'{illust.user.id}/{illust.user.id}-{illust.id}-{i}'


def callback(page: IllustsPage):
    for illust in page.illusts:
        print('downloading', illust.id)
        client.download_illust(illust)
        client.delete_bookmark(illust.id)


with PixivClient.refresh('refresh token') as client:
    client.filename_formatter = formatter
    client.get_user_bookmarks(callback)
```