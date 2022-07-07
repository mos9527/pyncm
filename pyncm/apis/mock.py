# -*- coding: utf-8 -*-
"""未定用途 API,暂留"""
from . import WeapiCryptoRequest
import json


@WeapiCryptoRequest
def MockWeblog(logs):
    """网页端 - 用户足迹接口 - reserved

    Args:
        logs (Any): 记录的用户足迹

    Returns:
        dict
    """
    return "/weapi/feedback/weblog", {"logs": json.dumps(logs)}
