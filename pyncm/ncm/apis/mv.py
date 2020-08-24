from . import WeapiCryptoRequest

@WeapiCryptoRequest
def GetMVInfo(mv_id, res=1080):
    '''
        Fetches MV Info

            id      :   The ID of the MV
            res     :   MV Resolution
    '''
    return '/weapi/song/enhance/play/mv/url',{"id":str(mv_id),"r":str(res)}


@WeapiCryptoRequest
def GetMVComments(mv_id, offset=0, limit=20,total=True):
    '''
        Fetches a album's comments.No VIP Level needed.

            offset  :   sets where the comment begins
            limit   :   sets how many of them can be sent
    '''            
    return '/weapi/v1/resource/comments/R_MV_5_%s' % mv_id,{"rid":"R_MV_5_%s" % mv_id,"offset":str(offset),"total":str(total).lower(),"limit":str(limit)}