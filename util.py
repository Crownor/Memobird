#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
@ Author : Yihan Guo
@ Mail   : crownor@icloud.com
@ File   : util.py
@ Date   : 2019-07-16
@ IDE    : PyCharm
@ Desc   : 各种工具
"""
from loguru import logger
import requests
import json
import hashlib
import base64
# from crypto.Cipher import DES
# from crypto.Util import Padding
from datetime import datetime

_timestamp = lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def post_request(url: str, data: dict) -> dict:
    """
    请求url，获得返回结果
    :param url: 要访问的url
    :param data: 要传的数据
    :return: 返回结果
    """
    resp = None
    _headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    try:
        if not url or not data:
            raise ValueError("POST请求值为空，url: " + url + "  data:" + str(data))
        r = requests.post(url=url, data=json.dumps(data), headers=_headers, timeout=(10, 10))
        resp = dict()
        r.raise_for_status()
        resp = r.json()
    except requests.exceptions.MissingSchema:
        logger.exception("POST请求URL格式不正确，请求的url为: " + url)
    except requests.exceptions.ConnectTimeout:
        logger.exception("POST 请求连接超时，请求URL为： " + url + " 数据为：" + str(data))
    except requests.exceptions.ReadTimeout:
        logger.exception("POST请求获取返回数据时失败，请求URL为： " + url + " 数据为：" + str(data))
    except requests.exceptions.ConnectionError:
        logger.exception("POST请求连接失败，请求URL为： " + url + " 数据为：" + str(data))
    except ValueError as e:
        logger.exception(e)
    except Exception as e:
        logger.exception("POST请求遭遇到异常，请求URL为： " + url + " 数据为：" + str(data) + "异常为：\n" + str(e))
    return resp


def merge_dicts(*dict_args) -> dict:
    """
    合并为一个新的字典
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


# def get_sec_key(date: datetime):
#     """
#     生成用于加解密的密钥
#     :param date: 日期
#     :return: 密钥
#     """
#     try:
#         time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
#     except ValueError:
#         time = datetime.strptime(date, '%Y/%m/%d %H:%M:%S')
#     date = time.strftime('%Y%m%d%H%M%S')
#     key = '4' + date[7:10] + '3' + date[8:11] + '9' + date[9:12] + '8' + date[10:13] + 'f676'
#     m = hashlib.md5()
#     m.update(key.encode())
#     key = m.hexdigest()[0:8]
#     return key
#
#
# def encrypt_message(message: str, date: datetime):
#     """
#     加密要发送的信息
#     :param message:要加密的信息
#     :param date: 日期
#     :return: 加密后的密文
#     """
#     byte_key = get_sec_key(date).encode()
#     w = DES.new(byte_key, DES.MODE_CBC, byte_key)
#
#     message = Padding.pad(message.encode(), 8, 'pkcs7')
#     message = w.encrypt(message)
#     message = base64.b64encode(message).decode().replace("+", "-")
#     return message
#
#
# def decrypt_message(message: str, date: datetime):
#     """
#     解密接收的信息
#     :param message: 要解密的信息
#     :param date: 日期
#     :return: 解密后的原文
#     """
#     byte_key = get_sec_key(date).encode()
#     w = DES.new(byte_key, DES.MODE_CBC, byte_key)
#
#     message = base64.b64decode(message.replace("-", "+").encode())
#     message = w.decrypt(message)
#     message = Padding.unpad(message, 8, 'pkcs7').decode()
#     return message
