import logging
import uuid
from importlib.machinery import SourceFileLoader
from typing import Dict, Any

from base import BaseExecutor
from models import ExecutorContext
import os
from logging.handlers import TimedRotatingFileHandler
import re
from logging_exception_formatter import LoggingExceptionFormatter

DEFAULT_LOG_FORMAT = '[%(asctime)s][%(levelname)s][%(name)s][%(filename)s:%(lineno)d] %(message)s'
DEFAULT_LOG_FORMAT_TEMPLATE = '{ "time": "%(asctime)s.%(msecs)03d", "level":"%(levelname)s", "msg":"%(message)s", "module":"%(name)s", "line":"%(filename)s:%(lineno)d", "from":"python_executor", "cloud_id":"--cloud_id", "user_id":"--user_id", "task_id":"--task_id", "subtask_id":"--subtask_id", "lot_no":"--lot_no", "label":"null", "public_ip":"--public_ip" }'


def invoke_for_debug(template_path: str, params: Dict[str, Any] = None):
    """Debug 调用启动"""
    fake_user_id = str(uuid.uuid4())
    fake_task_id = str(uuid.uuid4())
    fake_subtask_id = str(uuid.uuid4())
    fake_cloud_id = str(uuid.uuid4())
    fake_lot_no = '123456789'
    fake_public_id = '127.0.0.1'

    config_logging(fake_cloud_id, fake_user_id, fake_task_id, fake_subtask_id, fake_lot_no, logging.DEBUG,fake_public_id)

    module = SourceFileLoader("py_executor.executor", template_path).load_module()
    AtomExecutor = module.AtomExecutor

    executor: BaseExecutor = AtomExecutor(
        api_endpoint='',
        user_id=fake_user_id,
        task_id=fake_task_id,
        subtask_id=fake_subtask_id,
        lot_no=fake_lot_no,
        ctx=ExecutorContext(params),
        is_capture = False,
        debug=True,
    )

    executor.start()


def config_logging(cloud_id: str, user_id: str, task_id: str, subtask_id: str, lot_no: str, log_level: str, public_ip: str):
    try:
        DEFAULT_LOG_FORMAT = DEFAULT_LOG_FORMAT_TEMPLATE.replace("--task_id", task_id, 1).replace("--subtask_id", subtask_id, 1).replace("--user_id", user_id, 1).replace("--cloud_id", cloud_id, 1).replace("--lot_no", lot_no, 1).replace("--public_ip", public_ip, 1)
        defalut_formatter = LoggingExceptionFormatter(DEFAULT_LOG_FORMAT, datefmt='%Y-%m-%dT%H:%M:%S')
        dirs = "./logs/"
        os.makedirs(dirs, exist_ok=True)
        log_file_handler = TimedRotatingFileHandler(filename=dirs+'log', when="MIDNIGHT", interval=1, backupCount=30, encoding="utf-8")
        log_file_handler.suffix = "%Y-%m-%d.log"
        log_file_handler.extMatch = re.compile(r"\d{4}-\d{2}-\d{2}.log$")
        log_file_handler.setFormatter(defalut_formatter)
        log = logging.getLogger()
        log.setLevel(log_level)
        log.addHandler(log_file_handler)
    except Exception as err:
        print(err)
    # logging.basicConfig(level=log_level, format=DEFAULT_LOG_FORMAT)
