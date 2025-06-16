# surveyor/utils.py
import qrcode
import base64
from io import BytesIO
import random
import string
from .models import SurveyInContainer

def generate_unique_referal():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        if not SurveyInContainer.objects.filter(referal=code).exists():
            return code

def char_to_value(c):
    mapping = {
        'A': 10, 'B': 12, 'C': 13, 'D': 14, 'E': 15, 'F': 16,
        'G': 17, 'H': 18, 'I': 19, 'J': 20, 'K': 21, 'L': 23,
        'M': 24, 'N': 25, 'O': 26, 'P': 27, 'Q': 28, 'R': 29,
        'S': 30, 'T': 31, 'U': 32, 'V': 34, 'W': 35, 'X': 36,
        'Y': 37, 'Z': 38
    }
    if c.isdigit():
        return int(c)
    elif c.upper() in mapping:
        return mapping[c.upper()]
    else:
        raise ValueError(f"Karakter tidak valid: {c}")

def calculate_check_digit(container_no):
    total = 0
    for i, char in enumerate(container_no[:10]):
        val = char_to_value(char)
        total += val * (2 ** i)
    check_digit = total % 11
    return 0 if check_digit == 10 else check_digit

def is_valid_container(container_no):
    if len(container_no) != 11:
        return False
    expected_digit = calculate_check_digit(container_no)
    return expected_digit == int(container_no[-1])

def generate_qr_base64(data):
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"
