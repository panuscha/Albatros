import os
from pdf2image import convert_from_path

directory = 'PDFs'
for dirpath, _, filenames in os.walk(directory):
    filenames_to_process = len(filenames)
    for f in filenames:
        img_path = os.path.abspath(os.path.join(dirpath, f))
        filename = os.path.basename(f)[:-4]
        new_path =  f"JPGs/{filename}"
        if not os.path.exists(new_path) and filename != '.DS_S':
            print(filename)
            pages = convert_from_path(img_path)
            for i, page in enumerate(pages):
                if not os.path.exists(new_path):
                    os.makedirs(new_path)
                path = f"{new_path}/{filename}_{i}.jpg"
                page.save(path, "JPEG")