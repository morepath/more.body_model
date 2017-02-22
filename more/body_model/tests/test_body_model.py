import pytest
from webtest import TestApp as Client

import dectate
from more.body_model import BodyModelApp


def test_json_obj_load():
    class App(BodyModelApp):
        pass

    class Collection(object):
        def __init__(self):
            self.items = []

        def add(self, item):
            self.items.append(item)

    collection = Collection()

    @App.path(path='/', model=Collection)
    def get_collection():
        return collection

    @App.json(model=Collection, request_method='POST')
    def default(self, request):
        self.add(request.body_obj)
        return 'done'

    class Item(object):
        def __init__(self, value):
            self.value = value

    @App.load_json()
    def load_json(json, request):
        return Item(json['x'])

    c = Client(App())

    c.post_json('/', {'x': 'foo'})

    assert len(collection.items) == 1
    assert isinstance(collection.items[0], Item)
    assert collection.items[0].value == 'foo'


def test_json_obj_load_app_arg():
    class App(BodyModelApp):
        pass

    class Collection(object):
        def __init__(self):
            self.items = []

        def add(self, item):
            self.items.append(item)

    collection = Collection()

    @App.path(path='/', model=Collection)
    def get_collection():
        return collection

    @App.json(model=Collection, request_method='POST')
    def default(self, request):
        self.add(request.body_obj)
        return 'done'

    class Item(object):
        def __init__(self, value):
            self.value = value

    @App.load_json()
    def load_json(app, json, request):
        assert isinstance(app, App)
        return Item(json['x'])

    c = Client(App())

    c.post_json('/', {'x': 'foo'})

    assert len(collection.items) == 1
    assert isinstance(collection.items[0], Item)
    assert collection.items[0].value == 'foo'


def test_json_obj_load_default():
    class App(BodyModelApp):
        pass

    class Root(object):
        pass

    @App.path(path='/', model=Root)
    def get_root():
        return Root()

    @App.json(model=Root, request_method='POST')
    def default(self, request):
        assert request.body_obj == request.json
        return 'done'

    c = Client(App())

    c.post_json('/', {'x': 'foo'})


def test_json_body_model():
    class App(BodyModelApp):
        pass

    class Collection(object):
        def __init__(self):
            self.items = []

        def add(self, item):
            self.items.append(item)

    class Item1(object):
        def __init__(self, value):
            self.value = value

    class Item2(object):
        def __init__(self, value):
            self.value = value

    collection = Collection()

    @App.path(path='/', model=Collection)
    def get_collection():
        return collection

    @App.json(model=Collection, request_method='POST',
              body_model=Item1)
    def default(self, request):
        self.add(request.body_obj)
        return 'done'

    @App.load_json()
    def load_json(json, request):
        if json['@type'] == 'Item1':
            return Item1(json['x'])
        elif json['@type'] == 'Item2':
            return Item2(json['x'])

    c = Client(App())

    c.post_json('/', {'@type': 'Item1', 'x': 'foo'})

    assert len(collection.items) == 1
    assert isinstance(collection.items[0], Item1)
    assert collection.items[0].value == 'foo'

    c.post_json('/', {'@type': 'Item2', 'x': 'foo'}, status=422)


def test_json_obj_load_no_json_post():
    class App(BodyModelApp):
        pass

    class Root(object):
        pass

    @App.path(path='/', model=Root)
    def get_root():
        return Root()

    @App.json(model=Root, request_method='POST')
    def default(self, request):
        assert request.body_obj is None
        return 'done'

    c = Client(App())

    response = c.post('/', {'x': 'foo'})
    assert response.json == 'done'


def test_load_interaction():
    class App(BodyModelApp):
        pass

    @App.path(path='/')
    class Root(object):
        pass

    class A(object):
        pass

    class B(object):
        pass

    class Error(Exception):
        pass

    @App.load_json()
    def load_json(json, request):
        letter = json['letter']
        if letter == 'a':
            return A()
        elif letter == 'b':
            return B()
        else:
            raise Error()

    def load(request):
        return request.body_obj

    @App.json(model=Root, request_method='POST', load=load, body_model=A)
    def root_post_a(self, request, obj):
        assert request.body_obj is obj
        if isinstance(obj, A):
            return "this is a"
        assert False, "never reached"

    @App.json(model=Root, request_method='POST', load=load, body_model=B)
    def root_post_b(self, request, obj):
        assert request.body_obj is obj
        if isinstance(obj, B):
            return "this is b"
        assert False, "never reached"

    app = App()
    client = Client(app)

    r = client.post_json('/', {'letter': 'a'})
    assert r.json == "this is a"
    r = client.post_json('/', {'letter': 'b'})
    assert r.json == "this is b"
    with pytest.raises(Error):
        client.post_json('/', {'letter': 'c'})


def objects(actions):
    result = []
    for action, obj in actions:
        result.append(obj)
    return result


class Base(object):
    pass


class Foo(Base):
    pass


def test_view_body_model_querytool():
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


def test_load_json_querytool():
    class App(BodyModelApp):
        pass

    @App.load_json()
    def load(json, request):
        pass

    dectate.commit(App)

    r = objects(dectate.query_app(
        App, 'load_json'))

    assert r == [load]
