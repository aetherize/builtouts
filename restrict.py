from typing import Any, Callable

__all__ = ['restricted', 'restrictedMeta']


class restrictedMeta(type):
    def __init__(self, name: str, bases: tuple[type, ...], namespace: dict[str, Any]):
        self.__new__ = restrictedMeta.constructor(self)

    @staticmethod
    def constructor(this: type) -> Callable:
        def closure(cls, *pa, **kw) -> type:
            base = cls.__base__ if cls.__base__ != restricted else object
            if   pa and kw    : obj = base.__new__(cls, *pa, **kw)
            elif kw and not pa: obj = base.__new__(cls, **kw)
            elif pa and not kw: obj = base.__new__(cls, *pa)
            else              : obj = base.__new__(cls)
            if not cls.validator(obj):
                raise TypeError(cls.invalid(obj))
            return obj
        return closure

    def __instancecheck__(self, __instance: Any, /) -> bool:
        return isinstance(__instance, self.__base__) and getattr(self, 'validator')(__instance)


class restricted(metaclass=restrictedMeta):
    def validator(__instance: Any) -> bool:
        return bool()

    def invalid(__instance: Any) -> str:
        return str()


if __name__ == '__main__':
    class uint(int, restricted):
        def validator(__instance: Any) -> bool:
            if __instance >= 0:
                return True
            return False

        def invalid(__instance: Any) -> str:
            return f'Expected integer to be above 0, found {__instance} instead'

    a: uint = uint(5)

    tests = [
        ('a'),
        ('isinstance(a, int)'),
        ('isinstance(a, uint)'),
        ('isinstance(-1, int)'),
        ('isinstance(-1, uint)'),
    ]

    for x, test in enumerate(tests):
        eval("print(f'%i {%s = }')" % (x, test), globals())
