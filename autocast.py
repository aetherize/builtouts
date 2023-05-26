from typing  import Any, Callable, TypeVar, ParamSpec, cast
from inspect import getfullargspec, getcallargs

__all__ = ['autocast', 'realcast', 'cast']


T = TypeVar('T')
def realcast(_obj: Any, _to: type[T], force: bool = False) -> T:
    if not isinstance(_obj, _to):
        try:
            return cast(_to, _to(_obj))
        except:
            if force:
                raise TypeError(f'Could not cast \'{_obj}\' to {_to}')
    return cast(T, _obj)


P  = ParamSpec('P')
RT = TypeVar('RT')
def autocast(force: bool = False) -> Callable[[Callable[P, RT]], Callable[P, RT]]:
    """
    Function argument automatic casting at runtime, if `force` is set to True, will raise a TypeError on fail.\n
    Parameters or returns without type hints are ignored and passed directly.\n
    Usage :\n
    ```py
    @autocast(force=True)
    def foo(bar: int, baz: float) -> int:
        assert type(bar) == int
        assert type(baz) == float
        return bar + baz

    assert foo(5.0, '4.2') == 9
    ```
    """
    def decorator(fn: Callable[P, RT]) -> Callable[P, RT]:
        fnspec = getfullargspec(fn)
        types  = fnspec.annotations
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> RT:
            nargs  = list[Any]()
            mapped = getcallargs(fn, *args, **kwargs)

            for arg, val in mapped.items():

                caster = types.get(arg, None)

                if arg == fnspec.varargs:
                    nargs.extend(v if not caster else realcast(v, caster, force) for v in val)
                    continue

                if arg == fnspec.varkw:
                    kwargs.update({k: v if not caster else realcast(v, caster, force) for k,v in val})
                    continue

                if arg in fnspec.kwonlyargs:
                    kwargs[arg] = val if not caster else realcast(val, caster, force)
                    continue

                nargs.append(val if not caster else realcast(val, caster, force))

            nargs  = cast(type(args), nargs)
            result = fn(*nargs, **kwargs)
            caster = types.get('return', None)
            return result if not caster else realcast(result, caster, force)

        for attr in ('__name__', '__qualname__', '__annotations__', '__module__', '__doc__'):
            setattr(wrapper, attr, getattr(fn, attr, getattr(wrapper, attr)))
        return wrapper
    return decorator


if __name__ == '__main__':
    @autocast(force=True)
    def foo(bar: int, baz: float) -> int:
        """ Doc is preserved when wrapped at runtime
        """
        assert type(bar) == int
        assert type(baz) == float
        return bar + baz # type: ignore

    assert foo(5, '4.2') == 9 # type: ignore
