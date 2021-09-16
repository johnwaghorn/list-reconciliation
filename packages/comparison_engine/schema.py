import datetime
from typing import Any, Callable, Optional, Union

from dateutil import parser


class ConfigurationError(Exception):
    pass


class _Record:
    def __init__(self, data_dict: dict):
        self._data = data_dict

        found_pk = False
        for attr, obj in self._class_attrs:
            try:
                if getattr(obj, "primary_key") and found_pk:
                    raise ConfigurationError(
                        "Only one primary_key is allowed per record."
                    )

            except AttributeError:
                continue
            else:
                found_pk = True

        if not self.primary_key:
            raise ConfigurationError("Record must have exactly one primary_key.")

    def __getitem__(self, val: str) -> Union[Any, list[Any]]:
        def get_val(val):
            cols = getattr(self, val).val
            formatters = getattr(self, val).formatters

            if isinstance(cols, (list, tuple)):
                data = [self._data[col] for col in cols]
            else:
                data = self._data[cols]

            if isinstance(formatters, list):
                for formatter in formatters:
                    data = formatter(data)
            elif isinstance(formatters, Callable):
                data = formatters(data)

            return data

        if isinstance(val, list):
            return [get_val(v) for v in val]

        else:
            return get_val(val)

    @property
    def primary_key(
        self,
    ) -> Union[
        Optional[str], Optional[float], Optional[int], Optional[datetime.datetime]
    ]:
        for attr, obj in self._class_attrs:
            try:
                if getattr(obj, "primary_key"):
                    return self._data[getattr(self, attr).val]
            except AttributeError:
                continue

    @property
    def _class_attrs(self) -> list[tuple[str, Callable]]:

        return [i for i in self.__class__.__dict__.items() if not i[0].startswith("__")]


class LeftRecord(_Record):
    pass


class RightRecord(_Record):
    pass


class _Column:
    def __init__(self, val, primary_key=False):
        self.val = val
        self.primary_key = primary_key


class IntegerColumn(_Column):
    def __init__(self, val, primary_key=False):
        super().__init__(val, primary_key=primary_key)
        self.formatters = None


class FloatColumn(_Column):
    def __init__(self, val, primary_key=False):
        super().__init__(val, primary_key=primary_key)
        self.formatters = None


class StringColumn(_Column):
    def __init__(self, val, primary_key=False, formatters=None):
        super().__init__(val, primary_key=primary_key)
        self.formatters = formatters or None


class DateTimeColumn(_Column):
    def __init__(self, val, primary_key=False, formatters=None):
        super().__init__(val, primary_key=primary_key)
        self.formatters = formatters or (lambda x: parser.parse(str(x)))
