import dectate
from reg import methodify


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
