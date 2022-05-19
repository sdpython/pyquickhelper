"""
@file
@brief Helpers for unit tests.
"""
import numpy
import pandas


def getstate(obj, recursive=True, type_stop=None, type_stack=None, done=None):
    """
    Returns the state of an objects. It cannot be used
    to restore the object.

    :param obj: object
    :param recursive: unfold every object
    :param type_stop: stop recursion when type is in this list
    :param type_stack: list of types if an exception is raised
    :param done: already processed objects (avoids infinite recursion)
    :return: state (always as dictionay)
    """
    if done is not None and id(obj) in done:
        return id(obj)
    if obj is None:
        return None
    if type_stop is None:
        type_stop = (
            int, float, str, bytes,
            numpy.ndarray, pandas.DataFrame)
    if numpy.isscalar(obj):
        return obj
    if isinstance(obj, type_stop):
        return obj  # pragma: no cover

    if type_stack is None:
        type_stack = [type(obj)]
    else:
        type_stack = type_stack.copy()
        type_stack.append(type(obj))

    if done is None:
        done = set()
    done.add(id(obj))

    if type(obj) == list:
        state = [getstate(o, recursive=recursive, type_stop=type_stop,
                          type_stack=type_stack, done=done)
                 for o in obj]
        return state
    if type(obj) == set:
        state = set(getstate(o, recursive=recursive, type_stop=type_stop,
                             type_stack=type_stack, done=done)
                    for o in obj)
        return state
    if type(obj) == tuple:
        state = tuple(getstate(o, recursive=recursive, type_stop=type_stop,
                               type_stack=type_stack, done=done)
                      for o in obj)
        return state
    if type(obj) == dict:
        state = {a: getstate(o, recursive=recursive, type_stop=type_stop,
                             type_stack=type_stack, done=done)
                 for a, o in obj.items()}
        return state

    try:
        state = obj.__getstate__()
    except AttributeError as e:
        try:
            state = obj.__dict__.copy()
        except AttributeError as eee:  # pragma: no cover
            raise NotImplementedError(
                "Unable to retrieve state of object %r, type_stack=%r."
                "" % (type(obj), ", ".join(map(str, type_stack)))) from eee
        except Exception as ee:  # pragma: no cover
            raise NotImplementedError(
                "Unable to retrieve state of object %r, type_stack=%r."
                "" % (type(obj), ", ".join(map(str, type_stack)))) from ee
    except Exception as e:
        raise NotImplementedError(
            "Unable to retrieve state of object %r, type_stack=%r."
            "" % (type(obj), ", ".join(map(str, type_stack)))) from e

    if not recursive:
        return state  # pragma: no cover
    return getstate(state, recursive=True, type_stop=type_stop,
                    type_stack=type_stack, done=done)
