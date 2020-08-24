from . import WeapiCryptoRequest,LoginRequiredException,GetCurrentSession

@WeapiCryptoRequest
def GetPlaylistInfo(playlist_id,offset=0,total=True,limit=1000):
    '''Fetches a playlist's content'''
    return '/weapi/v6/playlist/detail',{"id":str(playlist_id),"offset":str(offset),"total":str(total).lower(),"limit":str(limit)}

@WeapiCryptoRequest
def GetUserPlaylists(user_id=0, offset=0, limit=1001):
    '''
        Fetches a user's playlists.No VIP Level needed.

            user_id :   The ID of the user.Set 0 for yourself (if logged in)
            offset  :   sets where the comment begins
            limit   :   sets how many of them can be sent
    '''
    if user_id == 0 and GetCurrentSession().login_info['success']:
        user_id = GetCurrentSession().login_info['content']['account']['id']
    elif user_id == 0:
        raise LoginRequiredException('A user ID or your login info is needed')
    return '/weapi/user/playlist',{'offset': str(offset), 'limit': str(limit),'uid': str(user_id)}