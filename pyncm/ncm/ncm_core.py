'''
# Netease Cloud Music Core

Core class for handling NCM API Calls
'''

import time
from typing import Type
import requests
import json
import re
import base64
from Crypto.Cipher import AES
from Crypto.Random import random
from hashlib import md5
import logging
from . import Depercated,logger,session

def DictPayload(func) -> dict:
    '''
        Wrapper for JSON responses
    '''
    def wrapper(*a,**k):
        response = None
        try:
            response = func(*a,**k)
            print('pass')
            if type(response) == requests.Response:
                try:
                    return json.loads(response.text)
                except Exception as e:
                    return e
            elif type(response) == str:
                try:
                    response = json.loads(response)
                    return response
                except Exception:
                    return response
            else:
                return response
        except Exception as e:
            logger.error('Error while executing %s:%s' % (func.__name__,e))
            return response
    return wrapper

class RSAPublicKey():
    '''
        RSA Publickey object

            N   :   modulus
            e   :   exponet
        All values are stored as integers
    '''
    def __init__(self, N, e):
        self.n = int(N, 16)
        self.e = int(e, 16)

class NeteaseCloudMusicKeygen():
    '''
        Implementation of the core.js's encryption functions in python

        Most importantly,the window.asrsea function,which generates encrypted text from keys

            random_keys     :       Whether uses random 2nd AES key or the constant 'mos9527ItoooItop' and its encypted RSA string
    '''

    def get_random_string(self, len):
        return ''.join([random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(0, len)])

    def AES_encrypt(self, data, key, iv,output_fmt='base64'):
        '''
            AES Encryption using CBC & zeropadding

                data        :       Data string to be encrypted
                key         :       Key string
                iv          :       IV Hex string
                output_fmt :       Output format ( 'base64' / 'hex' )

            ref:https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256
        '''
        bs = AES.block_size
        def pad2(s): return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
        encryptor = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
        encrypt_aes = encryptor.encrypt(str.encode(pad2(data)))
        formatter = {
            'base64':lambda d: str(base64.encodebytes(d), encoding='utf-8'),
            'hex':lambda d: d.hex().upper()
        }
        return formatter[output_fmt](encrypt_aes)

    def RSA_encrypt(self,data,pubkey:RSAPublicKey,reverse=True):
        '''
            A no-padding RSA encryption implemented in python
            Workings:    
               c ≡ n ^ e % N
               
                    c                :       result,the encrypted data
                    n(data)          :       Input
                    e(exponent)      :       RSA Exponent (Usually,10001 (bin) / 17 (decimal))
                    N(modulus)       :       RSA Modulus (aka pubkey)
            Usage:
                    data             :       Data string to be encrypted
                    pubkey           :       RSAPublicKey
                    reverse          :       Whether reverse the string when encrpyt or not
            ref:https://zh.wikipedia.org/wiki/RSA
        '''
        def toInt(s):return int(s.encode('utf-8').hex(),16)    
        n = data 
        if reverse:n = reversed(n)
        # Reverse the string.Big thanks to https://blog.csdn.net/weixin_30377461/article/details/97560323 for pointing this out
        n, e, N = toInt(''.join(n)), pubkey.e, pubkey.n
        return hex(n ** e % N)[2:].zfill(256)

    def __init__(self, random_key=False):
        self.generate_ncmcrypt = self.__call__
        self.aes_key = "0CoJUm6Qyw8W8jud"
        self.aes_iv = "0102030405060708"
        self.pubkey = RSAPublicKey(
            "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7",
            "10001"
        )
        # exponent 10001 and 258 bytes modulus (e,N)
        self.aes_key2 = "mos9527ItoooItop" if not random_key else self.get_random_string(16)
        self.encSecKey = "01a1c399271006da676da55763419f10f0e589515c49530b33418eec82202fc42dae0cd3aa4a2b7bdc3dafa7c6a918e405f3cdbc5d0349ef86913fc2dbe8764ed782e202e7828b547e85f6ae28b8b120bcf5fd3777a55731521612dcaff9813246a42876303b0f2307c9f264671ddc87159ff162e689fdfae5acb3af10250754" if not random_key else None
        '''
            Despite the second aes key is randomized in core.js,it's not necessary at all.
            If random_key is set,this key and it's RSA encrypted version will be generated once the generate function is called
            Then gets saved for later use
            E.g. if given 'mos9527ItoooItop' as the key,it will output the following:
                01a1c399271006da676da55763419f10f0e589515c49530b33418eec82202fc42dae0cd3aa4a2b7bdc3dafa7c6a918e405f3cdbc5d0349ef86913fc2dbe8764ed782e202e7828b547e85f6ae28b8b120bcf5fd3777a55731521612dcaff9813246a42876303b0f2307c9f264671ddc87159ff162e689fdfae5acb3af10250754
        '''

    def __call__(self, text):
        '''
            This part mimics the [window.asrsea] function.

            Geneartes NCMcrypted version of the text,outputs the [params] and [encSecKey] needed
        '''
        # 1st go,encrypt the text with aes_key and aes_iv
        params = self.AES_encrypt(text, self.aes_key, self.aes_iv)
        # 2nd go,encrypt the ENCRYPTED text again,with the 2nd key and aes_iv
        params = self.AES_encrypt(params, self.aes_key2, self.aes_iv)
        # 3rd go,generate RSA encrypted encSecKey
        if not self.encSecKey:
            self.encSecKey = self.RSA_encrypt(self.aes_key2, self.pubkey)
        return {
            'params': params,
            'encSecKey': self.encSecKey,
            'key2': self.aes_key2
        }

    def generate_hash(self, text):
        '''
            Generates a hash of the `utf-8` encoded hash digest
        '''
        HASH = md5(text.encode('utf-8'))
        return HASH.hexdigest()

class NeteaseCloudMusic():
    '''
        Using the cryptic API Netease implemented in

        thier muisc servers via mimicing what a NeteaseCloudMusic Web Client would Do
            
            log_callback    :       For logging.Uses simple_logger from ncm.strings,leave empty for not logging
            random_keys     :       Whether uses random 2nd AES key or the constant 'mos9527ItoooItop' and its encypted RSA string
        Functions inside are well commented,read them for more info.
    '''
    def __init__(self, random_keys=False):
        self.csrf_token, self.phone, self.password = '', '', ''
        # Cross-Site Reference Forgery token.Used for VIP validation & Phone number for login & password
        session.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "mos9527 Him Self/v15",
            "Referer":"https://music.163.com/"
        }
        # Headers required to fake a web client
        self.base_url = "https://music.163.com"
        # The base url to NE's music servers
        self.apis = {
            'meta_song': '/song',
            'meta_alubm': '/album',
            'detail': '/weapi/v3/song/detail',
            'wesong': '/weapi/song/enhance/player/url/v1',
            'playlist': '/weapi/v6/playlist/detail',
            'lyric': '/weapi/song/lyric',
            'login': '/weapi/login/cellphone',
            'comments_song': '/weapi/v1/resource/comments/R_SO_4_%s',
            'comments_album': '/weapi/v1/resource/comments/R_AL_3_%s',
            'comments_mv':'/weapi/v1/resource/comments/R_MV_5_%s',
            'user_playlists': '/weapi/user/playlist',
            'mv':'/weapi/song/enhance/play/mv/url'
        }
        # API URLs
        self.payloads = {
            # Note that all Song IDs are parsed as String,and the parameters passed must be in order
            'detail': r'{"c":"[{\"id\":\"%s\"}]","csrf_token":"%s"}',
            # Requires (Song ID,CSRF Token)
            'wesong': '{"ids":"[%s]","level":"%s","encodeType":"aac","csrf_token":"%s"}',
            # Requires (Song ID,Audio quality[standard,good,higher,lossless],CSRF Token)
            'playlist': '{"id":"%s","offset":"0","total":"true","limit":"1000","n":"1000","csrf_token":"%s"}',
            # Requires (Playlist ID,CSRF Token)
            'lyric': '{"id": "%s", "lv": -1, "tv": -1, "csrf_token": "%s"}',
            # Requires (Song ID,CSRF Token)
            'login': '{"phone":"%s","password":"%s","rememberLogin":"true","checkToken":"","csrf_token":""}',
            # Requires (Phone Number,Hashed(MD5) Password)
            'comments_song': '{"rid":"%s","offset":"%d","total":"true","limit":"%d","csrf_token":"%s"}',
            # Requires (Song ID,Comment Offset,Comment Limit,CSRF Token)
            'comments_album': '{"rid":"R_AL_3_%s","offset":"%s","total":"true","limit":"%s","csrf_token":"%s"}',
            # Requires (Album ID,Comment Offset,Comment Limit,CSRF Token)
            'comments_mv':'{"rid":"R_MV_5_%s","offset":"%s","total":"true","limit":"%s","csrf_token":"%s"}',
            # Requires (MV ID,Comment Offset,Comment Limit,CSRF Token)
            'user_playlists': '{offset: "%s", limit: "%s", uid: "%s", csrf_token: "%s"}',
            # Requires (Playlist Offset,Playlist count Limit,User ID,CSRF Token)
            'mv':'{"id":"%s","r":"%s","csrf_token":"%s"}',
            # Requires (MV ID,Resolution (1080,720,480,etc),CSRF Token)
        }
        # Call Formats
        self.keygen = NeteaseCloudMusicKeygen(random_keys)
        # Initalize keygen                 
        self.login_info = {'success': False,
                           'tick': time.time(), 'content': None}
        # Login info fetched in UpdateLoginInfo
        # Tick is saved to update login since the login info would expire
    def PerformRequest(self, *args, method='', extra_headers={}, extra_params={}) -> Type[requests.Response]:
        '''
            Posts to the server with the given args and method

            The method,args are described in self.callstack

            Returns a Response Object
        '''
        if not method:
            return None
        request_params = self.payloads[method] % args
        ncmcrypt = self.keygen(request_params)
        payload = {
            'params': ncmcrypt['params'],
            'encSecKey': ncmcrypt['encSecKey']
        }
        url = self.base_url
        if 'comments' in method:
            # Special Exceptions for non-standard arguments
            # which are also in URLs
            url += self.apis[method] % args[0]
        else:
            url += self.apis[method]
        r = session.post(
            url,
            headers={**session.headers, **extra_headers},
            params={'csrf_token': self.csrf_token, **extra_params},
            data=payload
        )
        return r
    @DictPayload
    def GetUserAccountLevel(self) -> str:
        '''
            Checks Login level,Returns the following values

                NOLOGIN     :   User haven't logged in yet
                USER        :   User logged in,but isn't VIP
                VIP         :   User logged in,and is VIP
        '''
        level = 'NOLOGIN'
        if not self.login_info['success']:
            logger.debug('User not logged in!')
            logger.debug('VIP Level operations will NOT be available')
        else:

            logger.debug('Logged in as %s' % self.login_info['content']['profile']['nickname'])
            if not self.login_info['content']['account']['vipType'] == 0:
                logger.debug('User has VIP privileges,continue...')
                level = 'VIP'
            else:
                logger.debug('User has no VIP privileges,continue...')
                level = 'USER'
        return level
    @DictPayload
    def UpdateLoginInfo(self, phone='', password='') -> dict:
        '''
            If given both phone number and password,updates them,and updates the cookies and the CSRF token

            Otherwise,if phone number and password are set,updates the cookies and the CSRF token

            Returns None if the response is invalid or the username & password combo is invalid

            Returns login info with structure tick/success/content that suggests the time/result/content of the attempt

            The value will be also set into the global variable to serve other functions
        '''
        if (phone and password):
            self.phone = phone
            self.password = password
            return self.UpdateLoginInfo()
            # Recursivly call the function to update cookies with the given account
        else:
            if (self.phone and self.password): 
                md5_password = self.keygen.generate_hash(self.password)
                # The password is first hashed then got sent to the server
                logger.debug('Attempting to login with hashed password %s...' % md5_password[:8])
                r = self.PerformRequest(self.phone, md5_password, method='login')
                try:
                    self.login_info = {'tick': time.time(), 'content': json.loads(r.text)}
                except Exception as e:
                    logger.error('Login failed with interal exception %s' % e)
                    return None
                # Try to parse the response into a JSON object. If failes,it means the response is invalid
                if not self.login_info['content']['code'] == 200:
                    logger.error('Loging failed with server exception' % self.login_info['content'])
                    self.login_info['success'] = False
                    return self.login_info
                # HTTP Response code will always be 200.The REAL response code lies in the JSON.
                # 200 means login successful
                # 415 means the IP was reqeusting too frequently.This can be solved with a delayed request
                # 502 means the combo provided is wrong
                self.login_info['success'] = True
                cookie = session.cookies.get_dict()
                self.csrf_token = cookie['__csrf']
                logger.debug('Updated login info for user %s' % self.login_info['content']['profile']['nickname'])               
                logger.debug('Updated cookies %s' % ','.join((cookie).keys()))
                self.GetUserAccountLevel()
                # Debugging,shows the user's account level
                return self.login_info
            else:
                logger.error('Not enough login info provided')
                return {}
    @DictPayload
    def GetSongDetail(self,song_id) -> requests.Response:
        '''
            Fetches a song's 'detailed' infomation

                song_id        :        ID of which song
        '''
        return self.PerformRequest(
            song_id, self.csrf_token, method='detail'
        )     
    @DictPayload
    @Depercated(replacement='NeteaseCloudMusic.GetSongDetail')
    def GetExtraSongInfo(self, song_id) -> dict:
        '''
            Fecthes a song's cover image,title,album and other meta infomation via webpage

            Which contains less infomation than 'GetSongDetail'  AND SLOWER

            This method is DEPERCATED

            Only using static webpage to decode the info.No APIs were used here
        '''
        url = self.base_url + self.apis['meta_song']
        r = session.get(url, params={'id': song_id}).text
        # Post url.This will give us the page contating infomations about the song
        regexes = {
            'regex_title': r"(?<=<meta property=\"og:title\" content=\").*(?=\")",
            'regex_cover': r"(?<=<meta property=\"og:image\" content=\").*(?=\")",
            'regex_author': r"(?<=由 ).*(?= 演唱)",
            'regex_album': r"(?<=收录于《).*(?=》专辑中)",
            'regex_album_id': r"(?<=<meta property=\"music:album\" content=\"https://music\.163\.com/album\?id=).*(?=\")",
            'regex_artist_id': r"(?<=<meta property=\"music:musician\" content=\"https://music\.163\.com/artist\?id=).*(?=\")",
        }
        # Regex is faster than lxml here,since it doesn't need to go through the whole document
        result = {'song_id': song_id}
        for key in regexes.keys():
            find = next(re.finditer(regexes[key], r, re.MULTILINE))
            try:                
                result[key[6:]] = find.group()
            except Exception:
                try:
                    result[key[6:]] = find.groups()
                except Exception as e:
                    logger.error('Exception' % key[6:] + ':' + e)
        return result
    @DictPayload
    def GetSongInfo(self, song_id, quality='lossless') -> requests.Response:
        '''
            Fetches a song's info.By default,it only returns the url and non-meta info.

                quality can be set to these values:
                    standard,higher,lossless
            VIP Level Required for such level operations

            Otherwise,it fallbacks to standard
        '''
        if not quality in ['standard', 'higher', 'lossless']:
            logger.warn('Invalid quality config `%s`,falling back to `standard`')
            quality = 'standard'
        #Quality check
        return self.PerformRequest(song_id, quality, self.csrf_token, method='wesong')
    @DictPayload
    def GetSongLyrics(self, song_id) -> requests.Response:
        '''
            Fetches a song's lyrics.No VIP Level needed
        '''
        return self.PerformRequest(
            song_id, self.csrf_token, method='lyric'
        )
    @DictPayload
    def GetPlaylistInfo(self, playlist_id) -> requests.Response:
        '''
            Fetches a playlist's content.No VIP Level needed
        '''
        return self.PerformRequest(
            playlist_id, self.csrf_token, method='playlist'
        )
    @DictPayload
    def GetSongComments(self, song_id, offset=0, limit=20) -> requests.Response:
        '''
            Fetches a song's comments.No VIP Level needed.

                offset  :   sets where the comment begins
                limit   :   sets how many of them can be sent
        '''
        return self.PerformRequest(
            song_id, offset, limit, self.csrf_token, method='comments_song'
        )
    @DictPayload
    def GetAlbumInfo(self, album_id) -> requests.Response:
        '''
            Fetches an album's info.Containing the list of the songs,the cover and etc

            No APIs were harmed during this process
        '''
        url = self.base_url + self.apis['meta_alubm']
        r = session.get(url, params={'id': album_id}).text
        # Post url.This will give us the page contating infomations about the album
        regexes = {
            'regex_songlist': r"(?<=<textarea id=\"song-list-pre-data\" style=\"display:none;\">).*(?=</textarea>)",
            'regex_description': r"(?<=<meta property=\"og:description\" content=\")[^\"]*(?=\")",
            'regex_title': r"(?<=<meta property=\"og:title\" content=\").*(?=\")",
            'regex_cover': r"(?<=<meta property=\"og:image\" content=\").*(?=\")",
            'regex_author': r"(?<=data-res-author=\").*(?=\")",
            'regex_release': r"(?<=<b>发行时间：</b>).*(?=</p)",
            'regex_publisher': r"(?<=<b>发行公司：</b>\n).*(?=\n)",
        }
        # Regex is faster than lxml here,since it doesn't need to go through the whole document
        find,result = (),{}
        for key in regexes.keys():
            try: 
                find = next(re.finditer(regexes[key], r, re.MULTILINE))               
                result[key[6:]] = find.group()
            except Exception:
                try:
                    result[key[6:]] = find.groups()
                except Exception as e:
                    logger.error('Exception' % key[6:] + ':' + e)
        try:
            result['songlist'] = json.loads(result['songlist'])
        except Exception as e:
            logger.error('Exception occured while procssing Album songlist' + ':' + e)
        return result
    @DictPayload
    def GetAlbumComments(self, song_id, offset=0, limit=20) -> requests.Response:
        '''
            Fetches a album's comments.No VIP Level needed.

                offset  :   sets where the comment begins
                limit   :   sets how many of them can be sent
        '''
        return self.PerformRequest(
            song_id, offset, limit, self.csrf_token, method='comments_album'
        )
    @DictPayload
    def GetUserPlaylists(self, user_id=0, offset=0, limit=1001) -> requests.Response:
        '''
            Fetches a user's playlists.No VIP Level needed.

                user_id :   The ID of the user.Set 0 for yourself (if logged in)
                offset  :   sets where the comment begins
                limit   :   sets how many of them can be sent
        '''
        if user_id == 0 and not self.GetUserAccountLevel() == 'NOLOGIN':
            user_id = self.login_info['content']['account']['id']
        elif user_id == 0:
            return {}
        return self.PerformRequest(
            offset, limit, user_id, self.csrf_token, method='user_playlists'
        )
    @DictPayload
    def GetMVInfo(self, id,res=1080) -> requests.Response:
        '''
            Fetches MV Info

                id      :   The ID of the MV
                res     :   MV Resolution
        '''
        return self.PerformRequest(
            id,res,self.csrf_token,method='mv'
        )
    @DictPayload
    def GetMVComments(self, mv_id, offset=0, limit=20) -> requests.Response:
        '''
            Fetches a album's comments.No VIP Level needed.

                offset  :   sets where the comment begins
                limit   :   sets how many of them can be sent
        '''
        return self.PerformRequest(
            mv_id, offset, limit, self.csrf_token, method='comments_mv'
        ) 