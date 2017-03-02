import morepath


class Request(morepath.Request):
    @morepath.reify
    def body_obj(self):
        """JSON object, converted to an object.

        You can use the :meth:`App.load_json` directive to specify
        how to transform JSON to a Python object. By default, no
        conversion takes place, and ``body_obj`` is identical to
        the ``json`` attribute.
        """
        if not self.is_body_readable:   # pragma: no cover
            return None
        if self.content_type != 'application/json':
            return None
        return self.app._load_json(self.json, self)
