import os
import cv2 as cv
from PIL import Image as im
import pytesseract
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .models import SkincareIngredient
from difflib import get_close_matches
from .preprocessing import binary_otsus, deskew  

# Halaman Upload Preview
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

# Proses OCR dengan preprocessing lengkap
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

        # Preprocessing Gambar
        image = cv.imread(full_path)
        binary_img = binary_otsus(image)  # Binarisasi Otsu
        processed_image = deskew(binary_img)  # Koreksi kemiringan
        cv.imwrite(full_path, processed_image)  # Simpan kembali gambar yang telah diproses

        # Ekstraksi Teks dengan OCR
        text = pytesseract.image_to_string(im.fromarray(processed_image))

        # Hapus file setelah OCR
        default_storage.delete(image_path)

        # Pencocokan bahan dengan database
        detected_ingredients = text.lower().split()
        db_ingredients = {ing.name.lower(): ing.benefit for ing in SkincareIngredient.objects.all()}

        for word in detected_ingredients:
            match = get_close_matches(word, db_ingredients.keys(), n=1, cutoff=0.7)
            if match:
                ingredients[match[0]] = db_ingredients[match[0]]

        return render(request, 'result.html', {'text': text, 'ingredients': ingredients})

    return redirect('home')
