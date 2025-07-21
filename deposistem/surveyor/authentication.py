from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from .external_user import ExternalUser

class QueryStringJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        token = request.GET.get('token')
        if token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        return super().authenticate(request)

    def get_user(self, validated_token):
        # Langsung pakai 'user_id' sebagai claim name
        user_id = validated_token.get('user_id')

        if user_id is None:
            raise exceptions.AuthenticationFailed('Token tidak mengandung user_id.')

        try:
            return ExternalUser.objects.get(id=user_id)
        except ExternalUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('User tidak ditemukan.')
