import cv2
import easyocr
import numpy as np
import re
from datetime import datetime
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deposistem.settings')
django.setup()

from surveyor.models import KontainerTerdeteksi 

# Inisialisasi OCR
reader = easyocr.Reader(['en'])

# Buka kamera
cap = cv2.VideoCapture(0)

print("📷 Arahkan kamera ke kertas yang berisi nomor kontainer (misal: MSCU1234567)")

# Set untuk menyimpan nomor yang sudah terdeteksi agar tidak dobel
detected_numbers = set()

# Ambil nomor dari database biar tidak dobel antar sesi
for obj in KontainerTerdeteksi.objects.all():
    detected_numbers.add(obj.nomor_kontainer)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = reader.readtext(frame)

    for (bbox, text, prob) in results:
        text_clean = text.replace(" ", "").replace("-", "").upper()

        # Cocokkan format nomor kontainer: 4 huruf + 6-7 angka
        if re.match(r'^[A-Z]{4}\d{6,7}$', text_clean):
            if text_clean not in detected_numbers:
                print(f"[DETEKSI] Nomor Kontainer: {text_clean} | Probabilitas: {prob:.2f}")
                detected_numbers.add(text_clean)

                # Simpan frame ke file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"kontainer_{text_clean}_{timestamp}.jpg"
                filepath = os.path.join('media/gambar_kontainer', filename)  # simpan ke folder media

                # Buat folder jika belum ada
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                cv2.imwrite(filepath, frame)
                print(f"📸 Gambar disimpan: {filepath}")

                # Simpan ke database
                kontainer = KontainerTerdeteksi(
                    nomor_kontainer=text_clean,
                    gambar=f"gambar_kontainer/{filename}",
                    probabilitas=prob,
                )
                kontainer.save()
                print("💾 Data disimpan ke database (model KontainerTerdeteksi)")

            # Gambar bounding box
            pts = [(int(x), int(y)) for x, y in bbox]
            cv2.polylines(frame, [np.array(pts)], isClosed=True, color=(0, 255, 0), thickness=2)
            cv2.putText(frame, text_clean, (pts[0][0], pts[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Deteksi Nomor Kontainer dari Kertas", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
