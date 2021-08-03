import json
from pathlib import Path
from enum import unique, IntEnum
from typing import Any, Optional, Tuple, Dict, Union, List
from utils import jsonify

from yarl import URL

__all__ = ['Proxy', 'ExecutorContext']


class ExecutorContext(object):
    _params: Dict

    def __init__(self, params: Any):
        self._params = params
        if not any(
            [
                isinstance(self._params, dict),
                "MainKeys" in self._params,
                isinstance(self._params.get("MainKeys"), list),  # 检查 MainKeys 是否是一个列表
            ]
        ):
            raise ValueError("this is a invalid params json or there are an invalid `MainKeys` parameter")

    @classmethod
    def from_path(cls, params_path: Path):
        return cls(json.loads(params_path.read_text()))

    def param(self, name) -> Union[str, List[str]]:
        return self._params.get(name, None)

    @property
    def main_keys(self) -> List[str]:
        return self.param("MainKeys")

    @main_keys.setter
    def main_keys(self, value: Any):
        raise AttributeError("the attribute is uneditable")

class Proxy(object):
    scheme: str = "http"  # ["http", "socks5", ...]
    user: Optional[str] = None
    pswd: Optional[str] = None
    host: str
    port: int

    proxy_id: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    expire: Optional[Any] = None

    def __init__(self, *, scheme="http", host="", port=None, user=None, password=None, **kwargs):
        self.scheme = scheme
        self.host = host
        self.port = port
        self.user = user
        self.pswd = password

        self.proxy_id = kwargs.get("proxy_id", None)
        self.source = kwargs.get("source", None)
        self.status = kwargs.get("status", None)
        self.expire = kwargs.get("expire", None)

    def as_uri(self) -> str:
        uri = URL.build(scheme=self.scheme, user=self.user, password=self.pswd, host=self.host, port=self.port)
        return str(uri)

    def as_dict(self) -> Dict[str, Union[str, int]]:
        """将 Proxy 对象转换为 dict"""
        return {
            "proxyId": self.proxy_id,
            "expire": self.expire,
            "source": self.source,
            "status": self.status,
            "scheme": self.scheme,
            "user": self.user,
            "password": self.pswd,
            "host": self.host,
            "port": self.port,
            "uri": self.as_uri(),
        }

    def as_proxies(self) -> Dict[str, str]:
        """返回 requests 形式的代理字典"""
        return {'http': self.as_uri(), 'https': self.as_uri()}

    def as_json(self) -> str:
        """将 Proxy 对象序列化为 JSON 字符串"""
        return jsonify(self.as_dict())

    @classmethod
    def from_dict(cls, value: Dict[str, Union[str, int]]):
        return cls(**value)

    @classmethod
    def from_json(cls, value: str):
        """从 json 字符串构建 Proxy 对象"""
        return cls.from_dict(json.loads(value))

    @property
    def auth(self) -> Tuple[Optional[str], Optional[str]]:
        return self.user, self.pswd

    @auth.setter
    def auth(self, value):
        raise AttributeError("this is a read-only attribute")

    @classmethod
    def from_uri(cls, value: str):
        uri = URL(value)
        return cls(scheme=uri.scheme, host=uri.host, port=uri.port, user=uri.user, password=uri.password)

    def __repr__(self):
        return f'Proxy("{self.as_uri()}")'