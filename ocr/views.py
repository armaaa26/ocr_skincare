import os
import re
import uuid
import cv2 as cv
from PIL import Image as im
import pytesseract
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from difflib import get_close_matches

from .models import SkincareIngredient
from .preprocessing import binary_otsus, deskew  # ⬅ hanya panggil, tidak tulis ulang

def home(request):
    return render(request, 'index.html')

def scan(request):
    return render(request, 'scan.html')

def upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        file_name = default_storage.save(os.path.join('uploads', image_file.name), ContentFile(image_file.read()))
        image_url = default_storage.url(file_name)
        return render(request, 'upload.html', {'image_url': image_url, 'image_path': file_name})
    return redirect('home')

def process_image(request):
    text = ""
    ingredients = {}

    if request.method == 'POST':
        image_path = request.POST.get('image_path')
        if not image_path:
            return redirect('home')

        full_path = os.path.join(settings.MEDIA_ROOT, image_path)
        if not os.path.exists(full_path):
            return redirect('home')

        # Baca gambar asli
        image = cv.imread(full_path)

        # Panggil fungsi preprocessing dari preprocessing.py
        binary_img = binary_otsus(image)      # Binarisasi Otsu
        processed_image = deskew(binary_img)  # Koreksi kemiringan

        # Simpan hasil gambar yang diproses ke file sementara (opsional)
        processed_filename = f"processed_{uuid.uuid4().hex}.png"
        processed_path = os.path.join(settings.MEDIA_ROOT, 'uploads', processed_filename)
        cv.imwrite(processed_path, processed_image)

        # OCR dari gambar hasil preprocessing
        text = pytesseract.image_to_string(im.fromarray(processed_image))

        # Deteksi kata-kata dari teks hasil OCR
        detected_words = re.findall(r'\b\w+\b', text.lower())

        # Ambil data dari database
        db_ingredients = SkincareIngredient.objects.all()
        matched_ingredients = set()

        for word in detected_words:
            if word in matched_ingredients:
                continue
            match = get_close_matches(word, [ing.name.lower() for ing in db_ingredients], n=1, cutoff=0.7)
            if match:
                try:
                    ing = SkincareIngredient.objects.get(name__iexact=match[0])
                    ingredients[ing.name] = {
                        'benefit': ing.benefit,
                        'side_effect': ing.side_effect,
                        'warning': ing.warning
                    }
                    matched_ingredients.add(match[0])
                except SkincareIngredient.DoesNotExist:
                    ingredients[match[0]] = {
                        'benefit': 'Tidak ditemukan di database.',
                        'side_effect': '-',
                        'warning': '-'
                    }
                    matched_ingredients.add(match[0])

        # Tampilkan gambar asli (warna), bukan hasil preprocessing
        image_url = default_storage.url(image_path)

        return render(request, 'result.html', {
            'text': text,
            'ingredients': ingredients,
            'image_url': image_url
        })

    return redirect('home')
