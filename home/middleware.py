from django.shortcuts import redirect


class RestrictAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and request.user.is_authenticated and not request.user.is_staff:
            return redirect('index')  # Redirect to index page if user is not staff
        return self.get_response(request)
