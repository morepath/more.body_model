import morepath


class View(morepath.view.View):
    def __call__(self, app, obj, request):
        super(View, self).__call__(app, obj, request)
        if self.load is not None:
            request.body_obj = self.load(request)
