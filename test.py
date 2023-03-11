from pyncm import apis
from bilibili_api import sync

async def main():
    print(await apis.artist.GetArtistDetails(artist_id=13499634))

sync(main())