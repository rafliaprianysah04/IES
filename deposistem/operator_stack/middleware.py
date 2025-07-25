from django.utils.deprecation import MiddlewareMixin
from .utils import get_user_from_token

class ExternalUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        Dipanggil sebelum view dijalankan, cocok untuk menanamkan user manual ke request.
        """
        user = get_user_from_token(request)
        if user:
            request.user = user