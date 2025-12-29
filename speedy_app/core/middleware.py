
import sys

class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only inspect the test upload path or admin upload path
        if 'upload' in request.path or 'admin' in request.path:
            # Debugging disabled for production
            pass

        response = self.get_response(request)
        return response
