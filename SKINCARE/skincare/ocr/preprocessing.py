import numpy as np
import cv2 as cv
from scipy.ndimage import interpolation as inter
from PIL import Image as im

def binary_otsus(image, filter: int = 1):
    """Binarisasi gambar menggunakan Otsu's Binarization"""
    if len(image.shape) == 3:
        gray_img = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    else:
        gray_img = image

    # Otsu's Binarization dengan atau tanpa Gaussian Blur
    if filter != 0:
        blur = cv.GaussianBlur(gray_img, (5, 5), 0)
        binary_img = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]
    else:
        binary_img = cv.threshold(gray_img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]

    return binary_img

def find_score(arr, angle):
    """Menghitung skor untuk sudut kemiringan gambar"""
    data = inter.rotate(arr, angle, reshape=False, order=0)
    hist = np.sum(data, axis=1)
    score = np.sum((hist[1:] - hist[:-1]) ** 2)
    return hist, score

def deskew(binary_img):
    """Mengoreksi kemiringan gambar (deskew)"""
    bin_img = (binary_img // 255.0)
    delta = 0.1
    limit = 3
    angles = np.arange(-limit, limit + delta, delta)
    scores = []

    for angle in angles:
        _, score = find_score(bin_img, angle)
        scores.append(score)

    best_angle = angles[scores.index(max(scores))]

    # Memperbaiki kemiringan gambar
    data = inter.rotate(bin_img, best_angle, reshape=False, order=0)
    img = im.fromarray((255 * data).astype("uint8"))
    pix = np.array(img)
    return pix

def vexpand(gray_img, color: int):
    """Menambahkan ruang kosong vertikal di gambar"""
    color = 1 if color > 0 else 0
    (h, w) = gray_img.shape[:2]
    space = np.ones((10, w)) * 255 * color
    return np.block([[space], [gray_img], [space]])

def hexpand(gray_img, color: int):
    """Menambahkan ruang kosong horizontal di gambar"""
    color = 1 if color > 0 else 0
    (h, w) = gray_img.shape[:2]
    space = np.ones((h, 10)) * 255 * color
    return np.block([space, gray_img, space])
