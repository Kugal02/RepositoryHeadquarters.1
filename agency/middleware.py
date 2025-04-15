from django.contrib import messages

class ClearMessagesOnLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Clear messages if we're rendering the login page after logout
        if request.path == '/login/' and request.user.is_anonymous:
            list(messages.get_messages(request))  # Accessing clears them

        return response
