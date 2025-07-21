from rest_framework_simplejwt.tokens import AccessToken
from .external_user import ExternalUser

def get_user_from_token(request):
    token_str = request.GET.get('token')
    if not token_str:
        return None

    try:
        token = AccessToken(token_str)
        user_id = token['user_id']
        user = ExternalUser.objects.filter(id=user_id).first()
        return user
    except Exception:
        return None
