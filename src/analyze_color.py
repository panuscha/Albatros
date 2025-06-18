from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
import os
from PIL import Image, ImageStat  

colors = set()

directory = 'PDFs'
for dirpath, dirnames, filenames in os.walk(directory):
    for filename in filenames:
        if filename != '.DS_Store':
            category = dirpath[5:]
            file = os.path.join(dirpath, filename)
            image = convert_from_path(file)
            image = image[0].convert("RGB")
            d = image.getdata()
            stats = ImageStat.Stat(image)
            print(f'{filename} {stats.mean}')
            # for item in d:
            #     print(item)

            
               