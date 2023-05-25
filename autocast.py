from typing  import Callable, TypeVar, ParamSpec
from inspect import getfullargspec, getcallargs

__all__ = ['autocast', 'cast']


O = TypeVar('O')
T = TypeVar('T')
def cast(_obj: O, _to: type[T] = None, force: bool = False) -> O | T:
    if _to and not isinstance(_obj, _to):
        try:
            return _to(_obj)
        except:
            if force: raise TypeError(f'Could not cast \'{_obj}\' to {_to}')
    return _obj


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
            nargs  = list()
            mapped = getcallargs(fn, *args, **kwargs)

            for arg, val in mapped.items():
                caster = types.get(arg, None)

                arg_is_kwargs = arg == fnspec.varkw
                if arg_is_kwargs:
                    kwargs.update({k: cast(v, caster, force) for k,v in val})
                    continue

                arg_is_nargs  = arg == fnspec.varargs
                if arg_is_nargs:
                    for v in val:
                        nargs.append(cast(v, caster, force))
                    continue

                arg_is_kwonly = arg in fnspec.kwonlyargs
                if arg_is_kwonly:
                    kwargs[arg] = cast(val, caster, force)
                else:
                    nargs.append(cast(val, caster, force))

            result = fn(*nargs, **kwargs) # type: ignore
            caster = types.get('return', None)
            return cast(result, caster, force)
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
