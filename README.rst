more.body_model: ``load_json`` infrastructure for Morepath
==========================================================

The idea is to recognize on an application-level what kind of JSON content
is being posted, and convert it into a Python object. You can use this
application object with ``request.body_obj``. With ``body_model`` you can
then write views that specifically match that kind model.

To use it you have to subclass your application from
``more.body_model.BodyModelApp``:

.. code-block:: python

  from more.body_model import BodyModelApp

  class App(BodyModelApp):
      pass

.. note:: If you want to use body_model on a mounted App, make sure that both,
the base App and the mounted App are a subclass from
``more.body_model.BodyModelApp``. Otherwise it will not work.


load_json
---------

The ``App.load_json`` directive lets you define a function that turns
incoming JSON into a Python object. This behavior is shared by all views in the
application. We detect JSON with the type field ``Item`` and interpret it as an
``Item`` instance, and pass through everything else:

.. code-block:: python

  @App.load_json()
  def load_json(json, request):
      if json.get('type') != 'Item':
          return json
      return Item(json['x'])

When you write a ``json`` view you automatically get the ``Item``
instance as the ``body_obj`` attribute of the ``request``:

.. code-block:: python

  @App.json(model=Collection, request_method='POST')
  def collection_post(self, request):
      collection.add(request.body_obj)
      return "success!"

You can write views that match on the class of ``body_obj`` by specifying
``body_model``:

.. code-block:: python

  @App.json(model=Collection, request_method='POST', body_model=Item)
  def collection_post_item(self, request):
      collection.add(request.body_obj)
      return "success!"


body_model
----------

To define JSON body conversion code generally for an application we can use
``App.load_json``:

.. code-block:: python

  @App.load_json()
  def load_json(json, request):
     if is_valid_document_json(json):
        return Document(title=json['title'],
                        author=json['author'],
                        content=json['content'])
     # fallback, just return plain JSON
     return json

Now we get a ``Document`` instance in ``Request.body_obj``, so
we can simplify ``document_collection_post``:

.. code-block:: python

  @App.json(model=DocumentCollection, request_method='POST')
  def document_collection_post(self, request):
      if not isinstance(request.body_obj, Document):
         raise webob.exc.HTTPUnprocessableEntity()
      result = self.add(request.body_obj)
      return request.view(result)

To only match if ``body_obj`` is an instance of ``Document`` we can
use ``body_model`` on the view instead:

.. code-block:: python

  @App.json(model=DocumentCollection, request_method='POST', body_model=Document)
  def document_collection_post(self, request):
      result = self.add(request.body_obj)
      return request.view(result)

Now you get the ``422`` error for free if no matching ``body_model``
can be found. You can also create additional ``POST`` views for
``DocumentCollection`` that handle other types of JSON content this
way.
