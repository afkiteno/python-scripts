from PIL import Image
import os

directory = os.path.join(os.path.dirname(__file__), "png")

for root, dirs, files in os.walk(directory):
    for filename in files:
        if filename.endswith(".jpg"):
            file_path = os.path.join(root, filename)
            
            with Image.open(file_path) as img:
                new_filename = os.path.splitext(filename)[0] + ".png"
                new_file_path = os.path.join(root, new_filename)
                
                img.save(new_file_path, "PNG")
            
            os.remove(file_path)