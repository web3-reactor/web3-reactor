"""
@TODO: config format checker.
"""
import typing as t
from functools import partialmethod
from io import StringIO
from pathlib import Path

import yaml

config_path = Path("config")
# 检查config文件夹是否存在，否则创建
if not config_path.exists():
    config_path.mkdir(parents=True)

T = t.TypeVar("T")


class ConfigScope(t.Dict):
    __name__: str
    __file__: Path
    __data__: t.Dict

    def __init__(self, name: str, defaults: t.Optional[t.Dict] = None):

        super().__init__()

        self.__data__ = {}
        self.__name__ = name
        if not name.endswith(".yaml"):
            self.__name__ += ".yaml"

        self.__file__ = config_path / self.__name__

        self.reload()

        if defaults:
            self.set_defaults(**defaults)

    # ===================== extend =====================

    def save(self):
        # 保存到文件
        with self.__file__.open('w', encoding='utf-8') as f:
            yaml.dump(self.__data__, f, allow_unicode=True)

    def reload(self):
        # 检查文件是否存在，不存在创建之
        if not self.__file__.exists():
            self.save()

        with self.__file__.open('r', encoding='utf-8') as f:
            self.__data__.clear()
            loaded = yaml.load(f, Loader=yaml.FullLoader)
            self.__data__.update(loaded if loaded else {})

    def set(self, name: str, value: t.Any):
        self.__setitem__(name, value)

    def set_default(self, name: str, value: t.Any):
        if name not in self.__data__:
            # trigger save
            self.__setitem__(name, value)

    def set_defaults(self, **kwargs):
        for k, v in kwargs.items():
            if k not in self.__data__:
                # not trigger save
                self.__data__.__setitem__(k, v)

        self.save()

    # ====================== dict ======================
    def __class_getitem__(cls, item: T) -> T:
        # for PEP 585
        return item

    def __getitem__(self, key):
        return self.__data__.__getitem__(key)

    def __setitem__(self, key, value):
        # will trigger save
        self.__data__.__setitem__(key, value)
        self.save()

    def __contains__(self, key):
        self.__dict__.__contains__(key)

    def get(self, name: str, default=None):
        return self.__data__.get(name, default)

    def values(self):
        return self.__data__.values()

    def items(self):
        return self.__data__.items()

    def keys(self):
        return self.__data__.keys()

    def update(self, other: t.Dict, **kwargs):

        if other:
            self.__data__.update(other)

        if kwargs:
            self.__data__.update(kwargs)

        self.save()

    def __eq__(self, other):
        """ Return self==value. """
        return id(self) == id(other)

    def __len__(self):
        return self.__data__.__len__()

    def __iter__(self):
        return self.__data__.__iter__()

    def __repr__(self):
        return f"<config {self.__name__}>"

    def __str__(self):
        temp_io = StringIO()
        yaml.dump(self.__data__, temp_io, allow_unicode=True)
        value = temp_io.getvalue()
        temp_io.close()
        return value

    # ==================== not implemented ====================

    def __not_implemented(self, *args, **kwargs):
        raise NotImplementedError("config is not a standard dict")

    clear = partialmethod(__not_implemented)
    copy = partialmethod(__not_implemented)
    fromkeys = partialmethod(__not_implemented)
    pop = partialmethod(__not_implemented)
    popitem = partialmethod(__not_implemented)
    setdefault = partialmethod(__not_implemented)
    __delitem__ = partialmethod(__not_implemented)
    __ge__ = partialmethod(__not_implemented)
    __gt__ = partialmethod(__not_implemented)
    __le__ = partialmethod(__not_implemented)
    __ior__ = partialmethod(__not_implemented)
    __ne__ = partialmethod(__not_implemented)
    __or__ = partialmethod(__not_implemented)
    __reversed__ = partialmethod(__not_implemented)
    __ror__ = partialmethod(__not_implemented)


__all__ = ("ConfigScope",)
