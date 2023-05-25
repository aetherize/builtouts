from typing  import Callable, TypeVar, ParamSpec
from inspect import getfullargspec, getcallargs

__all__ = ['autocast', 'cast']


U = TypeVar('U')
T = TypeVar('T')
def cast(_obj: U, _to: type[T] = None) -> T | U:
    if _to:
        try:
            return _to(_obj)
        except:
            pass
    return _obj


P  = ParamSpec('P')
RT = TypeVar('RT')
def autocast(fn: Callable[P, RT]) -> Callable[P, RT]:
    fnspec = getfullargspec(fn)
    types  = fnspec.annotations
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> RT:
        nargs  = list()
        mapped = getcallargs(fn, *args, **kwargs)

        for arg, val in mapped.items():
            caster = types.get(arg, None)

            arg_is_kwargs = arg == fnspec.varkw
            if arg_is_kwargs:
                kwargs.update({k: cast(v) for k,v in val})
                continue

            arg_is_nargs  = arg == fnspec.varargs
            if arg_is_nargs:
                for v in val:
                    nargs.append(cast(v, caster))
                continue

            arg_is_kwonly = arg in fnspec.kwonlyargs
            if arg_is_kwonly:
                kwargs[arg] = cast(val, caster)
            else:
                nargs.append(cast(val, caster))

        result = fn(*nargs, **kwargs) # type: ignore
        caster = types.get('return', None)
        return cast(result, caster)

    return wrapper


if __name__ == '__main__':
    @autocast
    def add(x: int, y: int) -> int:
        return x + y

    print(add('2', '3')) # type: ignore