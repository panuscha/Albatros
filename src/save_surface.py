import cv2
import pandas as pd
import fitz
import easyocr
import shapely
from shapely.ops import unary_union
import statistics
import os

age_category = ['3-5', '6-8','9-12'] # , '8+'

def compute_area(rectangles): 
    polygons = []
    num_parts = 0
    for rect in rectangles: 
        polygons.append(shapely.box(rect.top_left.x, rect.top_left.y, rect.bottom_right.x, rect.bottom_right.y)) 
    merged = unary_union(polygons)
    if merged.geom_type == "Polygon":
        num_parts = 1
        geoms_area = [merged.area]
    else:  
        num_parts = len(merged.geoms)
        geoms_area = [geom.area if geom.area < 100 else 100  for geom in merged.geoms]    
        
    return merged.area, num_parts, geoms_area 

def easy_ocr(reader, image_path):
    results = reader.readtext(image_path)
    d = pd.DataFrame(results, columns=['bbox', 'text', 'conf'])
    text = d['text'].tolist()
    raw_text = ' '.join(text).lower()
    return raw_text, d

def compute_area_ocr(ocr_results): 
    polygons = []
    for x in ocr_results.bbox: 
        polygons.append(shapely.box(x[0][0], x[0][1], x[2][0], x[2][1])) 
    merged = unary_union(polygons)
    if merged.geom_type == "Polygon":
        num_parts = 1
    else:  
        num_parts = len(merged.geoms)
        geoms_area = [geom.area for geom in merged.geoms]    
        
    return merged.area, num_parts, geoms_area 

def compute_text_area_pdf(book):
    pdf_file = f'PDFs/{book}.pdf'
    print(f'BOOK: {book.upper()}')
    
    if not os.path.isfile(pdf_file): return(0,0,0,0)
    doc = fitz.open(pdf_file)
    coverage_per_page = []
    boxes = []
    geoms_area_book = []

    for i in range(doc.page_count): 
        try:
            page = doc[i] 
            # Get text blocks
            text_instances = page.get_text("dict")["blocks"]

            # Get the PDF page dimensions
            page_rect = page.rect
            page_area = page_rect.width * page_rect.height

            rectangles = []
            # Draw rectangles for text spans
            for block in text_instances:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            rect = fitz.Rect(span["bbox"]) # scale to match rendered image
                            rectangles.append(rect)

            text_area, number_of_boxes, geoms_area = compute_area(rectangles)
            # Text coverage
            coverage_page = (text_area / (page_area)) * 100
            print(f"Page {i} — Coverage: {coverage_page:.2f}%, Boxes: {number_of_boxes}")
            coverage_per_page.append(coverage_page)
            boxes.append(number_of_boxes)
            geoms_area_book.append(geoms_area)
        
        except:  
            coverage_per_page.append(0)
            boxes.append(0)
            geoms_area_book.append(0)  
        coverage = statistics.fmean(coverage_per_page)  
    return (coverage, coverage_per_page, boxes, geoms_area_book)

def compute_text_area_ocr(book):
    JPG_file = f'JPGs/{book}/'
    conf = 0.40
    print(f'BOOK: {book.upper()}')
    
    reader = easyocr.Reader(['en'], gpu=True)
    book_image_surface = 0
    if not os.path.exists(JPG_file): return(0,0,0,0)
    number_of_pages = len(os.listdir(JPG_file))
    coverage_per_page = []
    boxes = []
    geoms_area_book = []
    for i in range(0, number_of_pages):
        try:
            test_img = f'{JPG_file}{book}_{i}.jpg'
            _, results = easy_ocr(reader, test_img)        

            im = cv2.imread(test_img)
            h, w, _ = im.shape
            image_surface = w * h
            book_image_surface += image_surface
            text_area, number_of_boxes, geoms_area = compute_area_ocr(results[results['conf'] > conf])
            coverage_page = text_area / image_surface * 100
            print(f"Page {i} coveres {coverage_page:.2f}% of the page and has {number_of_boxes} boxes.")
            coverage_per_page.append(coverage_page)
            boxes.append(number_of_boxes)
            geoms_area_book.append(geoms_area)
        except: 
            coverage_per_page.append(0)
            boxes.append(0)
            geoms_area_book.append(0)  
        coverage = statistics.fmean(coverage_per_page) 
    return (coverage, coverage_per_page, boxes, geoms_area_book)   

def both_versions():
    for method in ['PDF', 'OCR']:
        df = pd.read_excel('excel tables/Přehled vše2_rozdělané.xlsx') 
        df = df[df['je PDF'] == True & (df['Age'].isin(age_category))]
        results = df['Název knihy'].apply(lambda book: compute_text_area_pdf(book) if method == 'PDF' else compute_text_area_ocr(book) )
        df[['Coverage', 'Coverage per page', 'Boxes', 'Geoms_area']] = pd.DataFrame(results.tolist(), index=df.index)
        df2 = pd.read_excel(f'excel tables/{method} text surface area.xlsx') 
        df = pd.concat([df, df2], axis=0)
        df.to_excel(f'excel tables/{method} text surface area.xlsx')

both_versions()

