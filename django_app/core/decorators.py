from typing import Any

from django.utils.functional import classproperty


class cached_classproperty(classproperty):
    def get_result_field_name(self) -> str | None:
        return self.fget.__name__ + "_property_result" if self.fget else None

    def __get__(self, instance: Any, cls: Any | None = None) -> Any:
        result_field_name = self.get_result_field_name()

        if hasattr(cls, result_field_name):
            return getattr(cls, result_field_name)

        if not cls or not result_field_name:
            return self.fget(cls)

        setattr(cls, result_field_name, self.fget(cls))
        return getattr(cls, result_field_name)
