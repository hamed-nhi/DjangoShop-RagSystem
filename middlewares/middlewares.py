import threading

# Middleware to store the current request in thread local storage
# This allows models to access the current request if needed
#   Usage: In models, you can access the current request using:
#          from middlewares.middlewares import RequestMiddleware    

class RequestMiddleware:
    def __init__(self,get_response, thread_local=threading.local()):
        self.get_response = get_response
        self.thread_local = thread_local

    def __call__(self, request):
        self.thread_local.current_request = request
        response = self.get_response(request)
        return response