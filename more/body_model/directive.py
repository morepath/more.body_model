import dectate
from reg import methodify
from morepath import directive


def isbaseclass_notfound(a, b):
    # NOT_FOUND can happen in case of a fallback
    if a is dectate.NOT_FOUND:
        a = object
    return directive.isbaseclass(a, b)


class ViewAction(directive.ViewAction):
    filter_convert = {
        'body_model': dectate.convert_dotted_name
    }
    filter_convert.update(directive.ViewAction.filter_convert)
    filter_compare = {
        'body_model': isbaseclass_notfound
    }
    filter_compare.update(directive.ViewAction.filter_compare)


class LoadJsonAction(dectate.Action):
    config = {
    }

    app_class_arg = True

    def __init__(self):
        '''Register a function that converts JSON to an object.

        The decorated function gets ``app``, ``json`` and ``request``
        (:class:`morepath.Request`) arguments. The ``app`` argument is
        optional. The function should return a Python object based on
        the given JSON.
        '''
        pass

    def identifier(self, app_class):
        return ()

    def perform(self, obj, app_class):
        app_class._load_json = methodify(obj, selfname='app')
