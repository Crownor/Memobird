#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
@ Author : Yihan Guo
@ Mail   : crownor@icloud.com
@ File   : paper.py
@ Date   : 2019-07-17
@ IDE    : PyCharm
@ Desc   : 咕咕机的纸条类
"""

from __future__ import annotations
from typing import Dict, AnyStr
from loguru import logger
from datetime import datetime
from util import post_request
import base64
from io import BytesIO
from PIL import Image

_timestamp = lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# from typing import
class Paper(object):
    _BASE_URL = "http://open.memobird.cn/home/"
    IMAGE_MAX_WIDTH = 384

    def __init__(self, print_content_id: int = None, content: AnyStr = None, is_printed: bool = False,
                 device_id: AnyStr = None):
        """
        初始化纸条
        :type device_id: 在打印的设备ID
        :type is_printed: 是否已经打印
        :type content: 打印的内容
        :param print_content_id: 纸条的ID
        """
        self.print_content_id: int = print_content_id
        self.content: AnyStr = content
        self.is_printed: bool = is_printed
        self.device_id: AnyStr = device_id
        self.content: str = ''

    def update_printed_status(self, ak: AnyStr):
        """
        更新一下纸条的打印状态
        :type ak: 开发者账户ID
        :return:
        """
        if not self.print_content_id:
            self.is_printed = False
        url = self._BASE_URL + 'getprintstatus'
        data = dict(ak=ak, timestamp=_timestamp(), printcontentid=self.print_content_id)
        post_result: Dict
        post_result = post_request(url=url, data=data)
        if post_result['showapi_res_code'] != 1:
            logger.exception("在请求纸条ID：" + str(self.print_content_id) + "打印状态时网络出现问题")
        if post_result['printflag'] == 1:
            self.is_printed = True
        else:
            self.is_printed = False

    def add_text(self, text: str = '', bold: int = 0, font_size: int = 1, underline: int = 0):
        """
        添加文字
        :return:
        """
        if not text.endswith('\n'):
            text += '\n'
        # 先转GBK编码，然后base64，然后转回utf-8
        text = text.encode("gbk", 'replace')
        text = "T:" + base64.b64encode(text).decode()
        # content_to_add = self._get_new_item(base_text=text, bold=bold, font_size=font_size, icon_id=0, print_type=1,
        #                                     underline=underline)
        self.content += text

    def add_image(self, image: Image):
        """
        添加图片
        :param image:要添加的图片
        :return:
        """
        image = Image.open(image)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        width, height = image.size
        if width > self.IMAGE_MAX_WIDTH:
            image = image.resize((self.IMAGE_MAX_WIDTH, height * 384 // width),
                                 Image.ANTIALIAS)
        image = image.convert("1")
        p = BytesIO()
        image.save(p, "BMP")
        temp = base64.b64encode(p.getvalue()).decode("ascii")
        self.content += "|P:" + temp

    def get_content(self) -> str:
        """
        获取纸条要打印的内容
        :return: 要打印的内容
        """
        return self.content

    # @classmethod
    # def check_printed_status(cls, paper_id, ak):
    #     return "true"

    # @staticmethod
    # def _get_new_item(base_text: AnyStr = "IA0K", bold: int = 0, font_size: int = 1, icon_id: int = 0,
    #                   print_type: int = 1, underline: int = 0) -> Dict:
    #     """
    #     新添加要打印的项目
    #     :param base_text: 要打印的内容
    #     :param bold: 是否加粗
    #     :param font_size: 字体大小
    #     :param icon_id:
    #     :param print_type: 打印类型
    #     :param underline: 是否有下划线
    #     :return: 用于打印的数据
    #     """
    #     result = dict(base_text=base_text, bold=bold, font_size=font_size, icon_id=icon_id, print_type=print_type,
    #                   underline=underline)
    #     return result
