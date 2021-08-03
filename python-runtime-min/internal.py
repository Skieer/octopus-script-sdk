from typing import Dict, Any


def get_item(kwargs: Dict, type_cls: type, name: str, default=None) -> Any:
    value = kwargs.get(name, default)
    if not isinstance(value, type_cls):
        raise ValueError(f"item `{name}` is not a instance of {type_cls}")
    else:
        return value


def get_bool(kwargs: Dict, name: str, default=None) -> bool:
    return get_item(kwargs, bool, name, default)


def get_int(kwargs: Dict, name: str, default=None) -> int:
    return get_item(kwargs, int, name, default)


def get_str(kwargs: Dict, name: str, default=None) -> str:
    return get_item(kwargs, str, name, default)
