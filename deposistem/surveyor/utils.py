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
    

def char_to_num(char):
    values = {
        'A': 10, 'B': 12, 'C': 13, 'D': 14, 'E': 15, 'F': 16, 'G': 17, 'H': 18, 'I': 19,
        'J': 20, 'K': 21, 'L': 23, 'M': 24, 'N': 25, 'O': 26, 'P': 27, 'Q': 28, 'R': 29,
        'S': 30, 'T': 31, 'U': 32, 'V': 34, 'W': 35, 'X': 36, 'Y': 37, 'Z': 38
    }
    if char.isdigit():
        return int(char)
    return values.get(char.upper(), 0)

def calculate_check_digit(cont):
    total = 0
    factors = [2**i for i in range(10)]  # hanya 10 karakter pertama

    for i, char in enumerate(cont[:10]):
        total += char_to_num(char) * factors[i]
    
    return total % 11 if total % 11 != 10 else 0

def validate_container_id(cont):
    if len(cont) != 11:
        return False, None
    
    try:
        check_digit_actual = int(cont[-1])
    except ValueError:
        return False, None

    check_digit_calculated = calculate_check_digit(cont)
    return check_digit_calculated == check_digit_actual, check_digit_calculated

