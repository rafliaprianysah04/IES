import cv2
import easyocr
import numpy as np
import re
from datetime import datetime
import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deposistem.settings')
django.setup()

from surveyor.models import *

# Fungsi untuk menghitung Levenshtein Distance
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

# Inisialisasi OCR
reader = easyocr.Reader(['en'])

# Pastikan folder media/container_in/ ada
media_dir = os.path.join('media', 'container_in')
os.makedirs(media_dir, exist_ok=True)

# URL endpoint surveyin Django (ganti sesuai URL sebenarnya)
SURVEIN_URL = "http://127.0.0.1:8883/surveyor/?token={token}"
# Buka kamera
cap = cv2.VideoCapture(0)

print(" Arahkan kamera yang berisi nomor kontainer (misal: MSCU1234567)")

# Set untuk menyimpan nomor yang sudah terdeteksi
detected_numbers = set()


def is_valid_container_number(number):
    """
    Validasi nomor kontainer sesuai ISO 6346 (format AAAA1234567)
    """
    if not re.match(r'^[A-Z]{4}\d{7}$', number):
        return False

    # Konversi huruf ke angka sesuai tabel ISO
    char_map = {
        'A': 10, 'B': 12, 'C': 13, 'D': 14, 'E': 15, 'F': 16, 'G': 17, 'H': 18,
        'I': 19, 'J': 20, 'K': 21, 'L': 23, 'M': 24, 'N': 25, 'O': 26, 'P': 27,
        'Q': 28, 'R': 29, 'S': 30, 'T': 31, 'U': 32, 'V': 34, 'W': 35, 'X': 36,
        'Y': 37, 'Z': 38
    }

    weights = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]

    try:
        digits = []
        for i in range(10):  # hanya 10 karakter pertama
            c = number[i]
            if c.isalpha():
                value = char_map[c]
            else:
                value = int(c)
            digits.append(value)

        total = sum([a * b for a, b in zip(digits, weights)])
        check_digit = total % 11
        if check_digit == 10:
            check_digit = 0

        return check_digit == int(number[-1])
    except:
        return False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = reader.readtext(frame)
    zoomed_frame = None

    for (bbox, text, prob) in results:
        text_clean = text.replace(" ", "").replace("-", "").upper()

        #if re.match(r'^[A-Z]{4}\d{6,7}$', text_clean):
        if is_valid_container_number(text_clean):

            # Ambil bounding box dan crop untuk zoom
            pts = [(int(x), int(y)) for x, y in bbox]
            x_coords = [p[0] for p in pts]
            y_coords = [p[1] for p in pts]
            x_min, x_max = max(min(x_coords) - 20, 0), min(max(x_coords) + 20, frame.shape[1])
            y_min, y_max = max(min(y_coords) - 20, 0), min(max(y_coords) + 20, frame.shape[0])
            zoomed_frame = frame[y_min:y_max, x_min:x_max]

            if text_clean not in detected_numbers:
                print(f"[DETEKSI] Nomor Kontainer: {text_clean} | Probabilitas: {prob:.2f}")
                detected_numbers.add(text_clean)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"kontainer_{text_clean}_{timestamp}.jpg"
                filepath = os.path.join(media_dir, filename)
                cv2.imwrite(filepath, frame)
                print(f"Gambar disimpan: {filepath}")

                KontainerTerdeteksi.objects.create(
                    nomor_kontainer=text_clean,
                    gambar=f"container_in/{filename}",
                    probabilitas=prob
                )
                print(" Data disimpan ke database Django.")

                with open("nomor_kontainer_terdeteksi.txt", "a") as f:
                    f.write(f"{timestamp} - {text_clean}\n")
                print(" Teks disimpan ke 'nomor_kontainer_terdeteksi.txt'")

                try:
                    response = requests.post(SURVEIN_URL, data={'cont': text_clean})
                    print(f"Kirim ke surveyin, status code: {response.status_code}")
                except Exception as e:
                    print(f"Gagal kirim ke surveyin: {e}")

            # Gambar bounding box di tampilan asli
            cv2.polylines(frame, [np.array(pts)], isClosed=True, color=(0, 255, 0), thickness=2)
            cv2.putText(frame, text_clean, (pts[0][0], pts[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Jika ada hasil OCR, tampilkan zoom
    if zoomed_frame is not None and zoomed_frame.size > 0:
        zoomed_display = cv2.resize(zoomed_frame, (frame.shape[1], frame.shape[0]))
        cv2.imshow("Zoom Otomatis Nomor Kontainer", zoomed_display)
    else:
        cv2.imshow("Zoom Otomatis Nomor Kontainer", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
