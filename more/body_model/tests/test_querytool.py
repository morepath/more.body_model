import dectate
from morepath import core
from more.body_model import BodyModelApp, body_model_predicate
from more.body_model.app import body_model_unprocessable


def objects(actions):
    result = []
    for action, obj in actions:
        result.append(obj)
    return result


class Base(object):
    pass


class Foo(Base):
    pass


class Bar(Base):
    pass


def test_predicate_fallback():
    class App(BodyModelApp):
        pass

    dectate.commit(App)

    r = objects(dectate.query_app(App, 'predicate_fallback'))
    assert r == [
        core.model_not_found,
        core.name_not_found,
        core.method_not_allowed,
        body_model_unprocessable
    ]

    r = objects(dectate.query_app(App, 'predicate_fallback',
                                  dispatch='morepath.App.get_view'))
    assert r == [
        core.model_not_found,
        core.name_not_found,
        core.method_not_allowed,
        body_model_unprocessable
    ]

    # there aren't any predicates for class_path
    r = objects(dectate.query_app(
        App, 'predicate_fallback',
        dispatch='morepath.App._class_path'))
    assert r == []

    r = objects(dectate.query_app(App, 'predicate_fallback',
                                  func='morepath.core.model_predicate'))
    assert r == [
        core.model_not_found,
    ]


def test_predicate():
    class App(BodyModelApp):
        pass

    dectate.commit(App)

    r = objects(dectate.query_app(App, 'predicate'))
    assert r == [
        core.model_predicate,
        core.name_predicate,
        core.request_method_predicate,
        body_model_predicate
    ]

    r = objects(dectate.query_app(App, 'predicate',
                                  dispatch='morepath.App.get_view'))
    assert r == [
        core.model_predicate,
        core.name_predicate,
        core.request_method_predicate,
        body_model_predicate
    ]

    # there aren't any predicates for class_path
    r = objects(dectate.query_app(
        App, 'predicate',
        dispatch='morepath.App._class_path'))
    assert r == []

    r = objects(dectate.query_app(App, 'predicate',
                                  name='name'))
    assert r == [
        core.name_predicate
    ]

    r = objects(dectate.query_app(App, 'predicate',
                                  index='reg.ClassIndex'))
    assert r == [
        core.model_predicate,
        body_model_predicate
    ]

    r = objects(dectate.query_app(App, 'predicate',
                                  after='morepath.core.model_predicate'))
    assert r == [
        core.name_predicate
    ]


def test_view():
    class App(BodyModelApp):
        pass

    @App.json(model=Foo)
    def foo_default(self, request):
        pass

    @App.view(model=Base)
    def base_default(self, request):
        pass

    @App.view(model=Foo, name='edit')
    def foo_edit(self, request):
        pass

    dectate.commit(App)

    r = objects(dectate.query_app(App, 'view'))

    assert r == [core.standard_exception_view,
                 foo_default, base_default, foo_edit]

    r = objects(dectate.query_app(App, 'json'))

    assert r == [core.standard_exception_view,
                 foo_default, base_default, foo_edit]

    r = objects(dectate.query_app(
        App, 'view',
        model='morepath.tests.test_querytool.Base'))

    assert r == [base_default]

    r = objects(dectate.query_app(
        App, 'view',
        model='morepath.tests.test_querytool.Foo'))

    assert r == [foo_default, base_default, foo_edit]

    r = objects(dectate.query_app(
        App, 'view',
        model='morepath.tests.test_querytool.Bar'))

    assert r == [base_default]

    r = objects(dectate.query_app(
        App, 'view',
        name='edit'))

    assert r == [foo_edit]


def test_view_body_model():
    class App(BodyModelApp):
        pass

    @App.view(model=Foo, request_method='POST', body_model=Base)
    def foo_base(self, request):
        pass

    @App.view(model=Foo, request_method='POST', body_model=Foo)
    def foo_foo(self, request):
        pass

    dectate.commit(App)

    r = objects(dectate.query_app(
        App, 'view',
        model='morepath.tests.test_querytool.Foo',
        body_model='morepath.tests.test_querytool.Base'))

    assert r == [foo_base]

    r = objects(dectate.query_app(
        App, 'view',
        model='morepath.tests.test_querytool.Foo',
        body_model='morepath.tests.test_querytool.Foo'))
    assert r == [foo_base, foo_foo]


def test_dump_json():
    class App(BodyModelApp):
        pass

    @App.dump_json(model=Foo)
    def dump_foo(self, request):
        pass

    @App.dump_json(model=Bar)
    def dump_bar(self, request):
        pass

    dectate.commit(App)

    r = objects(dectate.query_app(
        App, 'dump_json'))

    assert r == [dump_foo, dump_bar]

    r = objects(dectate.query_app(
        App, 'dump_json',
        model='morepath.tests.test_querytool.Foo'))

    assert r == [dump_foo]

    r = objects(dectate.query_app(
        App, 'dump_json',
        model='morepath.tests.test_querytool.SubFoo'))

    assert r == [dump_foo]


def test_load_json():
    class App(BodyModelApp):
        pass

    @App.load_json()
    def load(json, request):
        pass

    dectate.commit(App)

    r = objects(dectate.query_app(
        App, 'load_json'))

    assert r == [load]
