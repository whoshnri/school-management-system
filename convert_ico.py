from PIL import Image

img = Image.open('assets/school-logo.jpeg')
# Save as ico, specifying sizes is good practice
icon_sizes = [(16,16), (32, 32), (48, 48), (64,64), (128, 128), (256, 256)]
img.save('assets/school-logo.ico', format='ICO', sizes=icon_sizes)
print("Conversion complete.")
