from dectate import directive
from reg import ClassIndex
from webob.exc import HTTPUnprocessableEntity
import morepath

from .request import Request
from . import directive as action


class App(morepath.App):
    request_class = Request
    load_json = directive(action.LoadJsonAction)

    def _load_json(self, json, request):
        """Load JSON as some object.

        By default JSON is loaded as itself.

        :param json: JSON (in Python form) to convert into object.
        :param request: :class:`morepath.Request`
        :return: Any Python object, including JSON.
        """
        return json


@App.predicate(morepath.App.get_view, name='body_model', default=object,
               index=ClassIndex, after=morepath.LAST_VIEW_PREDICATE)
def body_model_predicate(self, obj, request):
    """match request.body_obj with body_model by class.

    Predicate for :meth:`morepath.App.view`.
    """
    # optimization: if we have a GET request, a common case,
    # then there is no point in accessing the body.
    if request.method == 'GET':
        return None.__class__
    return request.body_obj.__class__


@App.predicate_fallback(morepath.App.get_view, body_model_predicate)
def body_model_unprocessable(self, obj, request):
    """if body_model not matched, 422.

    Fallback for :meth:`morepath.App.view`.
    """
    raise HTTPUnprocessableEntity()
