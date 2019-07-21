#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
@ Author : Yihan Guo
@ Mail   : crownor@icloud.com
@ File   : memobird.py
@ Date   : 2019-07-16
@ IDE    : PyCharm
@ Desc   : 咕咕机设备大类
"""
from __future__ import annotations
from loguru import logger
from util import post_request, merge_dicts
from datetime import datetime
from paper import Paper
from typing import List, Dict
import json

_timestamp = lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Memobird(object):
    _BASE_URL = "http://open.memobird.cn/home/"

    def __init__(self, ak: str):
        """
        初始化
        :param ak:开发者签名
        """
        if not ak:
            logger.error("初始化ACCESS_KEY时出错：ACCESS_KEY为空")
        if not isinstance(ak, str):
            logger.error("初始化ACCESS_KEY时出错：ACCESS_KEY类型不为str")
        self.ak: str = ak
        # 根据设备编号存储注册的用户及对应的api_userid
        self.devices: Dict[Dict[str, int]] = dict()
        # 根据咕咕号存储注册的设备及对应的api_userid
        self.users: Dict(Dict[str, int]) = dict()
        self.printed_papers: Dict[int, Paper] = dict()

    def __set_user_bind(self, memobird_id: str, useridentifying: str) -> int:
        """
        账号关联
        :param memobird_id: 咕咕机的设备编号
        :param useridentifying: 与咕咕平台进行关联的用户唯一标识符
        :return: api_userid
        """
        request_data = dict(ak=self.ak, timestamp=_timestamp(), memobirdID=memobird_id,
                            useridentifying=useridentifying)
        url = self._BASE_URL + "setuserbind"
        request_result = post_request(url=url, data=request_data)
        api_userid = request_result['showapi_userid']
        return api_userid

    def register_device(self, device_id: str, user_id: str):
        """
        在指定咕咕机上注册咕咕号
        :param device_id: 咕咕机设备号
        :param user_id: 咕咕号
        :return:
        """
        api_userid = self.__set_user_bind(memobird_id=device_id, useridentifying=user_id)
        # 首先在users里边加入
        if not self.users.__contains__(user_id):
            self.users[user_id] = dict()
        self.users[user_id][device_id] = api_userid

        if not self.devices.__contains__(device_id):
            self.devices[device_id] = dict()
        self.devices[device_id][user_id] = api_userid

    def get_devices_by_user_id(self, user_id: str) -> dict:
        """
        查询本地某咕咕号下注册的设备
        :param user_id: 咕咕号
        :return: 设备及对应的api_userid
        """
        if self.users.__contains__(user_id):
            return self.users[user_id]
        else:
            return None

    def get_users_by_devices(self, device_id: str) -> dict:
        """
        查询本地某咕咕机下绑定的账号
        :param device_id: 咕咕机设备号
        :return: 绑定的咕咕号及对应的api_userid
        """
        if self.devices.__contains__(device_id):
            return self.devices[device_id]
        else:
            return None

    def print_papers(self, papers: List[Paper], user_id: str, device_id: str) -> Dict[int, Paper]:
        # def print_papers(self, papers: list[Paper], user_id: str, device_id: str) -> dict(str):
        """
        根据咕咕号向指定绑定的设备发送指定的纸条
        :type device_id: 要用于打印的咕咕机设备号
        :param papers: 要打印的纸条
        :param user_id: 要打印纸条的咕咕号
        :return:打印的纸条序列号和对应的纸条以及打印状态
        """
        result_dic: Dict[int, Paper] = dict()
        if not self.users.__contains__(user_id):
            raise Exception("查询不到给定咕咕号")
        if not self.users[user_id].__contains__(device_id):
            raise Exception("给定咕咕号：" + user_id + "下无法查询到与设备：" + device_id + "的绑定")
        papers_id = None  # type:
        url = self._BASE_URL + "printpaper"
        data = dict(ak=self.ak, memobirdID=device_id, userID=self.users[user_id][device_id])
        each_paper: Paper
        for each_paper in papers:
            data['timestamp'] = _timestamp()
            data['printcontent'] = each_paper.get_content()
            each_post_result = post_request(url=url, data=data)
            if each_post_result['showapi_res_error'] != 'ok':
                logger.exception("打印纸条时出现错误：" + each_post_result['showapi_res_error'])
                continue
            if each_post_result['result'] != 1:
                logger.warning("纸条未打印")
            each_paper_id = each_post_result['printcontentid']
            self.printed_papers[each_paper_id] = each_paper
            result_dic[each_paper_id] = each_paper
        return result_dic

    def print_papers_to_all_binded_devices(self, user_id: str, papers: List[Paper]):
        """
        向给定咕咕号下所有绑定的设备打印纸条
        :type papers: 要打印的纸条
        :param user_id: 咕咕号
        :return: 打印的纸条序列号和对应的纸条以及打印状态
        """
        result_dic: Dict[int, Paper] = dict()
        if not self.users.__contains__(user_id):
            raise Exception("查询不到给定咕咕号")
        devices: Dict[str, int] = self.users[user_id]
        for each_device in devices:
            each_result = self.print_papers(papers=papers, user_id=user_id, device_id=each_device)
            result_dic = merge_dicts(result_dic, each_result)
        return result_dic

    # def _reformat_paper_content(self, paper: Paper, device_id: str, sender_id: str, receiver_id: str) -> str:
    #     """
    #     整理要打印的内容
    #     :param paper: 要打印的纸条
    #     :param device_id: 要打印的设备ID
    #     :param sender_id: 发送纸条的咕咕号
    #     :param receiver_id: 接收纸条的咕咕号
    #     :return: 要打印纸条的内容
    #     """
    #     receiver_id = sender_id if receiver_id == 0 else receiver_id
    #     date = _timestamp()
    #     device_id = encrypt_message(message=device_id, date=date)
    #     sender_id = encrypt_message(message=sender_id, date=date)
    #     receiver_id = encrypt_message(message=receiver_id, date=date)
    #     content = {
    #         "type": "1",
    #         "sysDate": date,
    #         "parameter": {
    #             "content": {
    #                 "strDate": date,
    #                 "content": {
    #                     "textList": paper.get_content()
    #                 },
    #                 "result": 0,
    #                 "packageCount": 1,
    #                 "smartGuid": device_id,
    #                 "userId": sender_id,
    #                 "msgType": 1,
    #                 "packageNo": 1,
    #                 "command": 3,
    #                 "toUserId": receiver_id,
    #                 "priority": 0
    #             },
    #             "datatype": "sendpaper"
    #         }
    #     }
    #
    #     result = {"msg": json.dumps(content)}
    #
    #     return result
