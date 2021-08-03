"""模版的父类

Example:
    一个简单的例子

    .. code-block:: python

       import requests
       from py_executor import BaseExecutor

       class AtomExecutor(BaseExecutor):  # 类名必须为 `AtomExecutor`
           name = "BaiduSpider"

           def process(self):
               r = requests.get("https://www.baidu.com")
               if not r.ok:
                   self.logger.warning("request failed")
               else:
                   data = {"text", r.text}
                   self.upload(data)
"""
import logging
import os
import sys
import time
from abc import ABC, abstractmethod
from threading import Thread
from typing import Dict, List, Optional

import psutil
import requests
from selenium.webdriver import Firefox, FirefoxOptions, Chrome, ChromeOptions
from yarl import URL

from models import ExecutorContext, Proxy
from utils import jsonify
from internal import get_bool, get_item, get_str
import json


class BaseExecutor(ABC):
    name: str = None  # 模版的名称 (作为)

    is_capture: bool = False
    debug: bool = False
    request_timeout = 5

    ctx: ExecutorContext
    user_id: str  # 用户 ID
    task_id: str  # 任务 ID
    subtask_id: str  # 自任务 ID
    lot_no: str  # 数据上传批次号
    api_endpoint: URL

    logger: logging.Logger

    def __init__(self, **kwargs):
        """
        :param str task_id:
        :param bool debug:
        :param str api_endpoint:
        :param ExecutorContext ctx:
        """
        logger_name = self.name
        if not logger_name:
            logger_name = self.__class__.__name__
            logging.getLogger(logger_name).warning(f"模版没有设置 `name`, 默认使用 `{logger_name}`")

        self.logger = logging.getLogger(logger_name)
        self.user_id = get_str(kwargs, "user_id")
        self.task_id = get_str(kwargs, "task_id")
        self.subtask_id = get_str(kwargs, "subtask_id")
        self.lot_no = get_str(kwargs, "lot_no")
        self.is_capture = get_bool(kwargs, "is_capture")
        self.debug = get_bool(kwargs, "debug")
        self.api_endpoint = URL(get_str(kwargs, "api_endpoint"))

        self.ctx = get_item(kwargs, ExecutorContext, "ctx")
        if not self.ctx:
            raise TypeError("missing required argument")

        self.check_parent()

        self.init()

    @abstractmethod
    def init(self):
        """初始化过程
        模版自行实现
        """
        pass

    def check_parent(self):
        """检查父进程是否退出
        如果父进程异常退出则直接结束该进程
        """

        def _check_parent():
            parent_pid = os.getppid()
            while True:
                if psutil.pid_exists(parent_pid):
                    time.sleep(1)  # 每秒检测一次
                else:
                    self.logger.error("Parent process exited abruptly. child process is ending...")
                    sys.exit(1)

        Thread(target=_check_parent, daemon=True).start()

    def start(self):
        self.logger.info(f"starting to process task {self.task_id}")
        self.process(self.ctx.main_keys)

    def process(self, main_keys: List[str]):
        try:
            for key in main_keys:
                self.process_item(key)
        except Exception as e:
            self.logger.error(e)
        finally:
            self.finish()

    @abstractmethod
    def process_item(self, key: str):
        raise NotImplementedError

    def upload(self, data: Dict):
        data_aggregation = {}
        data_aggregation['uniqueColumns'] = []
        data_aggregation['data'] = data
        self.logger.info(f"uploaded: {jsonify(data_aggregation)}")

    def get_firefox_driver(self, proxy: Optional[Proxy] = None) -> Firefox:
        options = FirefoxOptions()
        options.headless = not self.debug
        options.set_preference('dom.webdriver.enabled', False)  # 不设置 window.navigator.webdriver
        options.set_preference('browser.privatebrowsing.autostart', True)  # 以无痕模式启动

        if isinstance(proxy, Proxy):
            if proxy.scheme == 'http':
                options.set_preference('network.proxy.type', 1)  # Proxy type: manual
                options.set_preference('network.proxy.http', proxy.host)
                options.set_preference('network.proxy.http_port', proxy.port)
                self.logger.info(f"Firefox will launch with proxy: {proxy.as_uri()}")
            else:
                self.logger.warning(f"Not use proxy({proxy.as_uri()}): proxy type `{proxy.scheme}` not yet supported")

        self.logger.info('Firefox browser is launching...')
        return Firefox(options=options)

    def get_chrome_driver(self, proxy: Optional[Proxy] = None) -> Chrome:
        options = ChromeOptions()
        options.headless = not self.debug
        options.add_argument('incognito')  # 以无痕模式启动
        # 不设置 window.navigator.webdriver，类似于 firefox 的 dom.webdriver.enabled=false
        # 但是这里实际上依赖了 ChromeDriver 的一个 bug，ChromeDriver 79.0.3945.16 及以后版本失效
        # Ref: https://chromedriver.storage.googleapis.com/79.0.3945.16/notes.txt
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('no-sandbox')  # Docker 环境中启动必须使用 --no-sandbox 参数，否则会 crash
        options.add_argument('disable-gpu')  # 禁止 gpu 加速
        options.add_argument('disable-dev-shm-usage')  # 不使用 /dev/shm

        if isinstance(proxy, Proxy):
            if proxy.scheme == 'http':
                options.add_argument(f'proxy-server={proxy.host}:{proxy.port}')
                self.logger.info(f"Chromium will launch with proxy: {proxy.as_uri()}")
            else:
                self.logger.warning(f"Not use proxy({proxy.as_uri()}): proxy type `{proxy.scheme}` not yet supported")

        self.logger.info("Chromium browser is launching...")
        return Chrome(options=options)


    def finish(self):
        """完成时调用
        """
        if self.debug:
            self.logger.info(f"finished: task  {self.task_id}::{self.subtask_id}")
            return

    def capture(self):
        dir_path = os.path.abspath('capture')
        if os.path.exists(dir_path):
            os.mkdir(dir_path)
        filename = f'{self.subtask_id}_{int(time.time() * 1000)}.jpeg'
        abs_filename = os.path.join(dir_path, filename)
        # todo 这里截图
        # self.upload_capture_img(full_filename)
        return abs_filename

    def upload_capture_img(self, filepath):
        data = {'img_path': filepath}
        self.logger.info(f"upload_capture_img: {json.dumps(data)}")
