"""
一些常用的工具库
"""
import base64
import collections
import functools
import inspect
import json
import os
import warnings
from pathlib import Path
from typing import Any, Dict, Optional

import umsgpack
from Crypto.Cipher import AES


def deprecated(reason):
    if isinstance(reason, str):
        def decorator(func_1):
            if inspect.isclass(func_1):
                msg_1 = 'Call to deprecated class {name} ({reason}).'
            else:
                msg_1 = 'Call to deprecated function {name} ({reason}).'

            @functools.wraps(func_1)
            def wrapper_1(*args, **kwargs):
                warnings.simplefilter('always', DeprecationWarning)
                warnings.warn(msg_1.format(name=func_1.__name__, reason=reason), category=DeprecationWarning)
                warnings.simplefilter('default', DeprecationWarning)
                return func_1(*args, **kwargs)

            return wrapper_1

        return decorator

    elif inspect.isclass(reason) or inspect.isfunction(reason):
        func_2 = reason
        if inspect.isclass(func_2):
            msg_2 = 'Call to deprecated class {name}.'
        else:
            msg_2 = 'Call to deprecated function {name}.'

        @functools.wraps(func_2)
        def wrapper_2(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn(msg_2.format(name=func_2.__name__, ), category=DeprecationWarning)
            warnings.simplefilter('default', DeprecationWarning)
            return func_2(*args, **kwargs)

        return wrapper_2


class MetaProperty(property):
    def __init__(self, meta=None, **kwargs):
        super().__init__(**kwargs)
        self.meta = meta if meta is not None else {}


def config_property(env_name, default=None, cache_to: Optional[Path] = None, getter=lambda x: x) -> MetaProperty:
    """配置属性

    :param env_name: 环境变量的 Key
    :param default: 当没有该环境变量时的默认值
    :param cache_to: 缓存此配置到文件 cache_to 文件 (json 格式)
    :param getter: 从环境变量读取时的取值方法
    """

    def cache_setter(obj, value):
        """向 property 写入值时，写入缓存文件中"""
        if cache_to:  # 缓存文件中存在该值且其不为空时，直接返回该配置
            if not cache_to.exists():
                cache_to.write_text("{}")
        cache_config = json.loads(cache_to.read_text('utf8'))
        cache_config[env_name] = value
        cache_to.write_text(jsonify(cache_config))

    def env_getter(obj):
        if cache_to:  # 缓存文件中存在该值且其不为空时，直接返回该配置
            if not cache_to.exists():
                cache_to.write_text("{}")
            try:
                cache_config = json.loads(cache_to.read_text('utf8'))
                if env_name in cache_config and cache_config[env_name] is not None:
                    return cache_config[env_name]
            except ValueError as e:
                raise RuntimeError(f"配置文件 `{cache_to.as_posix()}` 不是有效的 JSON 文件: {e}")

        # 从环境变量中获取配置
        env_value = os.getenv(env_name)
        if not env_value:
            env_value = default
        else:
            env_value = getter(env_value)

        # 如果需要缓存，则写入回缓存文件中
        if cache_to:
            cache_setter(obj, env_value)

        return env_value

    def read_only_setter(obj, value):
        raise AttributeError("The attribute is read-only")

    f_getter = env_getter
    f_setter = cache_setter if cache_to else read_only_setter

    return MetaProperty(fget=f_getter, fset=f_setter)


def json_property(fn=None, *, name=None):
    if fn is None:
        return functools.partial(json_property, name=name)
    name = fn.__name__ if not name else name
    return MetaProperty(fget=fn, meta={'name': name})


class JsonEntity(object):
    def to_dict(self) -> Dict[str, Any]:
        result = dict()

        cls = self.__class__
        for prop_name in dir(cls):
            prop = getattr(cls, prop_name)
            if isinstance(prop, MetaProperty):
                prop_value = getattr(self, prop_name)
                if isinstance(prop_value, JsonEntity):
                    prop_value = prop_value.to_dict()
                result.update({prop.meta.get('name'): prop_value})

        return result

    def to_json(self) -> str:
        return jsonify(self.to_dict())


class DispatchingFormatter:
    def __init__(self, formatters, default_formatter):
        self._formatters = formatters
        self._default_formatter = default_formatter

    def format(self, record):
        formatter = self._formatters.get(record.name, self._default_formatter)
        return formatter.format(record)


def msgpack_encode(obj: Any) -> bytes:
    return umsgpack.packb(obj)


def msgpack_decode(data: bytes) -> Any:
    return umsgpack.unpackb(data)


def jsonify(obj: Any, sort_key=False):
    """将对象转换为 JSON 字符串
    """
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=sort_key)


# JSON 字符串 => OrderedDict
json_ordered_loads = functools.partial(json.loads, object_pairs_hook=collections.OrderedDict)


class Singleton(type):
    """单例模式元类

    Examples:
        一个简单的使用示例：

        .. code-block:: python

           class MyClass(object, metaclass=Singleton):
               def __init__(self, *args, **kwargs):
                   pass

        单例模式继承的示例：

        >>> class MyClassA(object, metaclass=Singleton):
        ...     def __init__(self):
        ...         self.num = 1
        >>> class MyClassB(MyClassA):
        ...     pass
        >>> obj_a1 = MyClassA()
        >>> obj_a2 = MyClassA()
        >>> obj_a1.num
        1
        >>> obj_a1.num += 5
        >>> obj_a2.num
        6
        >>> obj_b1 = MyClassB()
        >>> obj_b2 = MyClassB()
        >>> obj_b1.num
        1
        >>> obj_b2.num += 3
        >>> obj_b1.num
        4
        >>> obj_a1.num
        6
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
