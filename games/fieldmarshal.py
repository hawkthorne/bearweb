import inspect
import StringIO
import json
import copy


def _get_user_attributes(cls):
    boring = dir(type('dummy', (object, ), {}))
    return [item
            for item in inspect.getmembers(cls)
            if item[0] not in boring]


def _default_value(t):
    if t == unicode:
        return ''
    elif t == bool:
        return False
    elif t == int:
        return 0
    elif t == float:
        return 0.0
    elif t == long:
        return 0L
    elif t is None:
        return None
    elif type(t) == list:
        return []
    elif type(t) == dict:
        return {}
    elif type(t) == type and issubclass(t, Struct):
        return t()
    else:
        raise ValueError("Unsupported type {}".format(t))


def _dict_load(klass, payload):
    for name, value in _get_user_attributes(klass):
        if name in payload:
            if type(value) == type and issubclass(value, Struct):
                payload[name] = _dict_load(value, payload[name])
    return klass(**payload)


def _dict_repr(obj):
    output = {}
    for name, klass in _get_user_attributes(obj.__class__):
        if isinstance(getattr(obj, name), Struct):
            output[name] = _dict_repr(getattr(obj, name))
        else:
            output[name] = getattr(obj, name)
    return output


def _construct(value, struct):
    """A struct here can be the following types:

    int, unicode, list, dict, bool, None, Struct

    All other types are not valid
    """
    if type(struct) == list:

        if type(value) != list:
            raise ValueError("{} should be a {}".format(value, struct))

        if len(struct) > 1:
            raise ValueError("Struct lists can't be longer than 1")

        # No type in the list, so just accept the list and move on
        if len(struct) == 0 or len(value) == 0:
            return value

        return [_construct(item, struct[0]) for item in value]

    if type(struct) == dict:

        if type(value) != dict:
            raise ValueError("{} should be a {}".format(value, struct))

        if len(struct) > 1:
            raise ValueError("Struct dicts can't have more than 1 key")

        # No type in the list, so just accept the dict and move on
        if len(struct) == 0 or len(value) == 0:
            return value

        k_struct, v_struct = struct.items()[0]

        payload = {}

        for k, v in value.items():
            payload[_construct(k, k_struct)] = _construct(v, v_struct)

        return payload

    # Check if a Struct
    if type(struct) == type and issubclass(struct, Struct):
        if type(value) == dict:
            return struct(**value)

        if isinstance(value, struct):
            return value

        raise ValueError("Dict needed to initialize")

    if struct not in [unicode, bool, None, float, int, long]:
        raise ValueError("'{}' is not a supported type".format(struct))

    if not isinstance(value, struct):
        raise ValueError("'{}' is not of type {}".format(value, struct))

    return value


class Struct(object):

    def __init__(self, *args, **kwargs):
        attrs = _get_user_attributes(self.__class__)

        types = {k: v for k, v in attrs}

        for name, klass in attrs:
            if name not in kwargs:
                setattr(self, name, _default_value(klass))

        for key, value in kwargs.items():
            setattr(self, key, _construct(value, types[key]))


def dump(obj, file_object):
    file_object.write(dumps(obj))


def dumpd(obj):
    """Dump a struct as a Python dictionary"""
    return copy.deepcopy(obj.__dict__)


def dumps(obj):
    return json.dumps(_dict_repr(obj))


def load(klass, file_object):
    payload = json.load(file_object)
    return _dict_load(klass, payload)


def loads(klass, text):
    return load(klass, StringIO.StringIO(text))
