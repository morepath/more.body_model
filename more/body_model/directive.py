import dectate
from reg import methodify
from morepath import directive
from .view import View


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

    def perform(self, obj, template_engine_registry, app_class):
        render = self.render
        if self.template is not None:
            render = template_engine_registry.get_template_render(
                self.template, render)
        v = View(obj, render, self.load, self.permission, self.internal,
                 self.code_info)
        app_class.get_view.register(v, **self.key_dict())


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
