from PIL import Image
import cv2 #pip install opencv-python
import pytesseract #pip install pytesseract

image_path = 'screenshot.png'
# Load an image using Pillow (PIL)
image = Image.open(image_path)

# Perform OCR on the image
text = pytesseract.image_to_string(image)

print(text)

print('=====================================================')

image = cv2.imread(image_path)
# Convert to grayscale (optional, but often helpful)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
text = pytesseract.image_to_string(gray, lang='eng', config='--psm 6') 

# Print the extracted abstract
print(text)