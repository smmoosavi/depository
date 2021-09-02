from django.http import HttpResponse


class CheckDepository:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.user.is_authenticated and not request.user.is_superuser:
            if request.user.last_depository_id != request.META.get('HTTP_DEPOSITORY_ID', None):
                return HttpResponse(status=468)
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
