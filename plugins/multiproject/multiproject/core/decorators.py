"""
Module for some common decorators, for deprecation of a method and defining a class as
singleton to name a few.
"""

def singleton(cls):
    """
    Defines a class to be a singleton. Creates the decorated class if it's not already
    found, otherwise returns an instance from internal list.
    """
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


def deprecated(func):
    """
    Define a function to be deprecated. This prints a warning to the config class'
    logger facility when a function is used.

    Idea gotten from http://wiki.python.org/moin/PythonDecoratorLibrary

    Frame inspection info http://docs.python.org/library/inspect.html#the-interpreter-stack

    .. NOTE::

        This is slow, and on some aspects a dangerous decorator. Use only on methods that
        you have refactored out and want to keep backwards compatability for potential
        calls, that you've missed. Do *not* use the decorator just because you want to
        remove the function in future.

    """
    def wrapper(*args, **kwargs):
        import inspect
        from multiproject.core.configuration import Configuration

        caller_info = "<unknown>"
        frames = None

        try:
            frames = inspect.stack()

            if frames:
                # Caller info is the second frame
                caller = inspect.getframeinfo(frames[1][0])
                module = inspect.getmodule(frames[1][0])
                caller_info = "%s.%s():%d" % (module.__name__, caller[2], caller[1])
        except Exception, e:
            caller_info = str(e)
        finally:
            # Deleting the frames reference is apparently important. Otherwise this might affect stack
            # dumps in cases where a real exception is raised
            if frames:
                del frames

        conf = Configuration.instance()
        conf.log.warning("Deprecated call %s.%s() from %s" %
                         (func.__module__, func.__name__, caller_info))
        return func(*args, **kwargs)

    return wrapper
