# -*- coding: utf-8 -*-
"""Some all purpose utilities"""

class Singleton(type):
    """Singleton as metaclass
    >>> class Foo(object):
    ...     __metaclass__ = Singleton
    >>> a = Foo()
    >>> b = Foo()
    >>> a is b
    True
    >>> a.stuff = 'bar'
    >>> b.stuff
    'bar'
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def ParentMonkeyPatch(name, bases, namespace):
    """Monkey patching a parent class
    >>> class A(object):
    ...     def result(self):
    ...         return 0
    >>> class B(A):
    ...     __metaclass__ = ParentMonkeyPatch
    ...     def result(self):
    ...         return 1
    ...     def new_meth(self):
    ...         return self.__previous_result() + 1
    >>> x = A()
    >>> x.result()
    1
    >>> x.new_meth()
    1
    """
    assert len(bases) == 1, "Exactly one base class required"
    base = bases[0]
    for name, value in namespace.iteritems():
        if name != '__metaclass__':
            previous = getattr(base, name, None)
            if previous is not None:
                setattr(base, '__previous_'+name, previous)
            setattr(base, name, value)
    return base
