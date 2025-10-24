"""
pytest -o log_cli=true -o log_cli_level=INFO -W ignore::DeprecationWarning
pytest-asyncio模块的loop管理策略与pyncm-async的session管理策略存在冲突，使用 run_until_complete 进行异步函数的测试。


对于更合理的 assert 方式 assert res.get("code", None) == 200，部分接口在参数错误时仍会返回 code=200，不使用assert方式测试。
"""

import logging, json, pytest, asyncio
import pyncm_async
from pyncm_async.apis import *


logging.basicConfig(level=logging.INFO)

session_str = "PYNCM..."

album_id = 28516
artist_id = 9272
song_id = 286970
playlist_id = 2804505435
user_id = 14179251276
mv_id = 38020


def res_logging(res, api_name):
    logging.info((api_name, res.get("code", None), type(res), len(res), res.keys(), len(json.dumps(res))))

async def session_init():
    pyncm_async.SetCurrentSession(
        pyncm_async.LoadSessionFromString(session_str)
    )


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(session_init())
    yield loop

def test_album_GetAlbumInfo(event_loop: asyncio.AbstractEventLoop):
    logging.info(id(event_loop))
    res = event_loop.run_until_complete(album.GetAlbumInfo(album_id))
    res_logging(res, "GetAlbumInfo")

def test_album_GetAlbumComments(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(album.GetAlbumComments(album_id))
    res_logging(res, "GetAlbumComments")

def test_artist_GetArtistAlbums(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(artist.GetArtistAlbums(artist_id))
    res_logging(res, "GetArtistAlbums")

def test_artist_GetArtistTracks(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(artist.GetArtistTracks(artist_id))
    res_logging(res, "GetArtistTracks")

def test_artist_GetArtistTracks(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(artist.GetArtistTracks(artist_id))
    res_logging(res, "GetArtistTracks")

def test_artist_GetArtistDetails(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(artist.GetArtistDetails(artist_id))
    res_logging(res, "GetArtistDetails")

def test_cloud_GetCloudDriveInfo(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(cloud.GetCloudDriveInfo(50, 0))
    res_logging(res, "GetCloudDriveInfo")

def test_cloud_GetCloudDriveItemInfo(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(cloud.GetCloudDriveItemInfo([293931]))
    res_logging(res, "GetCloudDriveItemInfo")

def test_cloud_upload(event_loop: asyncio.AbstractEventLoop):
    # TODO
    pass

def test_cloud_SetRectifySongId(event_loop: asyncio.AbstractEventLoop):
    # TODO
    # 此 API 已测试通过。
    pass

def test_cloudsearch(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(
        cloudsearch.GetSearchResult("愚人的国度", cloudsearch.SONG)
    )
    res_logging(res, "GetSearchResult")

def test_login(event_loop: asyncio.AbstractEventLoop):
    # TODO
    # 除 Cookies 登录外，其它登录方式已测试通过。
    # login 模块登录外功能未测试。
    pass

def test_playlist_GetPlaylistInfo(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(playlist.GetPlaylistInfo(playlist_id))
    res_logging(res, "GetPlaylistInfo")

def test_playlist_GetPlaylistAllTracks(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(playlist.GetPlaylistAllTracks(playlist_id))
    res_logging(res, "GetPlaylistAllTracks")

def test_playlist_GetPlaylistComments(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(playlist.GetPlaylistComments(playlist_id))
    res_logging(res, "GetPlaylistComments")

def test_playlist_SetManipulatePlaylistTracks(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(
        playlist.SetManipulatePlaylistTracks([2120125578], 406884341, "add")
    )
    res_logging(res, "SetManipulatePlaylistTracks.add")
    res = event_loop.run_until_complete(
        playlist.SetManipulatePlaylistTracks([2120125578], 406884341, "del")
    )
    res_logging(res, "SetManipulatePlaylistTracks.del")

def test_playlist_create_and_remove(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(playlist.SetCreatePlaylist("PYNCM"))
    res_logging(res, "SetPlaylist.create")
    id = res["id"]
    res = event_loop.run_until_complete(playlist.SetRemovePlaylist((id)))
    res_logging(res, "SetPlaylist.remove")

def test_track_GetTrackDetail(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(track.GetTrackDetail(song_id))
    res_logging(res, "GetTrackDetail")

def test_track_GetTrackAudio(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(track.GetTrackAudio(song_id))
    res_logging(res, "GetTrackAudio")

def test_track_GetTrackAudioV1(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(track.GetTrackAudioV1(song_id))
    res_logging(res, "GetTrackAudioV1")

def test_track_GetTrackDownloadURL(event_loop: asyncio.AbstractEventLoop):
    # 已弃用
    pass

def test_track_GetTrackDownloadURLV1(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(track.GetTrackDownloadURLV1(song_id))
    res_logging(res, "GetTrackDownloadURLV1")

def test_track_GetTrackLyrics(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(track.GetTrackLyrics(song_id))
    res_logging(res, "GetTrackLyrics")

def test_track_GetTrackLyricsV1(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(track.GetTrackLyricsV1(song_id))
    res_logging(res, "GetTrackLyricsNew")

def test_track_GetTrackComments(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(track.GetTrackComments(song_id))
    res_logging(res, "GetTrackComments")

def test_track_SetLikeTrack(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(track.SetLikeTrack(2706275303, True))
    res_logging(res, "SetLikeTrack.add")
    res = event_loop.run_until_complete(track.SetLikeTrack(2706275303, False))
    res_logging(res, "SetLikeTrack.del")

def test_track_GetMatchTrackByFP(event_loop: asyncio.AbstractEventLoop):
    # TODO
    pass

def test_user_GetUserDetail(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(user.GetUserDetail(user_id))
    res_logging(res, "GetUserDetail")

def test_user_GetUserPlaylists(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(user.GetUserPlaylists(user_id))
    res_logging(res, "GetUserPlaylists")

def test_user_GetUserAlbumSubs(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(user.GetUserAlbumSubs())
    res_logging(res, "GetUserAlbumSubs")

def test_user_GetUserArtistSubs(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(user.GetUserArtistSubs())
    res_logging(res, "GetUserArtistSubs")

def test_user_SetSignin(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(user.SetSignin())
    res_logging(res, "SetSignin")

def test_user_SetWeblog(event_loop: asyncio.AbstractEventLoop):
    logs = [
        {
            "action": "play",
            "json": {
                "download": 0,
                "end": "interrupt",
                "id": song_id,
                "sourceId": album_id,
                "time": 60,
                "type": "song",
                "wifi": 0,
                "source": "list",
            },
        }
    ]
    res = event_loop.run_until_complete(user.SetWeblog(logs))
    res_logging(res, "SetWeblog")

def test_video_GetMVDetail(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(video.GetMVDetail(mv_id))
    res_logging(res, "GetMVDetail")

def test_video_GetMVResource(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(video.GetMVResource(mv_id))
    res_logging(res, "GetMVResource")

def test_video_GetMVComments(event_loop: asyncio.AbstractEventLoop):
    res = event_loop.run_until_complete(video.GetMVComments(mv_id))
    res_logging(res, "GetMVComments")
