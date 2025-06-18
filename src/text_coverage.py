import fitz
from shapely import box
from shapely.ops import unary_union
from collections import defaultdict
import pandas as pd


def compute_text_coverage(page):
    page_area = page.rect.width * page.rect.height

    # Extract all characters with their bounding boxes
    chars = page.get_text("dict")["blocks"]
    char_rects = []

    for block in chars:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                for char in span.get("chars", []):
                    char_rects.append(fitz.Rect(char["bbox"]))

    # Calculate total text-covered area
    text_area = sum(r.get_area() for r in char_rects)
    number_of_boxes = len(char_rects)
    coverage = (text_area / page_area) * 100

    return round(coverage, 2), number_of_boxes

def compute_area(rectangles): 
    top_left_wide = 0.98
    bottom_right_wide = 1.02
    polygons = []
    for rect in rectangles: 
        polygons.append(box(rect.top_left.x * top_left_wide, rect.top_left.y * top_left_wide, rect.bottom_right.x * bottom_right_wide, rect.bottom_right.y * bottom_right_wide)) 
    merged = unary_union(polygons)
    if merged.geom_type == "Polygon":
        num_parts = 1
        geoms_area = [merged.area]
    else:  
        num_parts = len(merged.geoms)
        geoms_area = [geom.area for geom in merged.geoms]    
        
    return merged, merged.area, num_parts, geoms_area 

def link_text_together(merged, spans, font, geometries_texts):
    if merged.geom_type == "Polygon":
        geometries_texts[(font,0)] = spans
        return geometries_texts
    for i, geom in enumerate(merged.geoms):
        for span in spans:
            x = span['bbox']
            rect = box(x[0] , x[1], x[2], x[3])
            if geom.contains(rect):
                geometries_texts[(font,i)].append(span)
    return geometries_texts



def compute_area_pdf_fonts(rectangles): 
    top_left_wide = 0.983
    bottom_right_wide = 1.018
    geoms_area = []
    merged_all = []
    merged_area = 0
    num_parts = 0
    geometries_texts = defaultdict(list)
    for font, values in rectangles.items():
        polygons = []
        for span in values: 
            x = span['bbox']
            polygons.append(box(x[0] , x[1]*top_left_wide, x[2], x[3]*bottom_right_wide)) 
            #polygons.append(shapely.box(rect.top_left.x * top_left_wide, rect.top_left.y * top_left_wide, rect.bottom_right.x * bottom_right_wide, rect.bottom_right.y * bottom_right_wide)) 
        merged = unary_union(polygons)
        geometries_texts = link_text_together(merged, values, font, geometries_texts)
        merged_all.append(merged) 
        if merged.geom_type == "Polygon":
            num_parts += 1
            geoms_area.append(merged.area)
            merged_area += merged.area
        else:  
            num_parts += len(merged.geoms)
            geoms_area.extend([geom.area for geom in merged.geoms])  
            merged_area += merged.area  
        
    return merged_all, merged_area, num_parts, geoms_area, geometries_texts 



def compute_area_ocr(ocr_results): 
    polygons = []
    geoms_area = []
    for x in ocr_results.bbox: 
        polygons.append(box(x[0][0], x[0][1], x[2][0], x[2][1])) 
    merged = unary_union(polygons)
    if merged.geom_type == "Polygon":
        num_parts = 1
    else:  
        num_parts = len(merged.geoms)
        geoms_area = [geom.area for geom in merged.geoms]    
        
    return merged.area, num_parts, geoms_area 
    
def easy_ocr(reader, image_path):
    results = reader.readtext(image_path)
    d = pd.DataFrame(results, columns=['bbox', 'text', 'conf'])
    text = d['text'].tolist()
    raw_text = ' '.join(text).lower()
    return raw_text, d


def preprocess_text(text):
    # Remove unwanted characters and normalize whitespace
    whitespaces = len(''.join(['a' if c.isspace() else '' for c in text]))
    non_whitespaces = len(''.join([c for c in text if not c.isspace()]))
    if whitespaces >=  (non_whitespaces+non_whitespaces)*0.35:
        text = text.replace('  ', '$')
        text = text.replace(' ', '')
        text = text.replace('$', ' ')
    text = text.strip().replace('\n', ' ').replace('\r', ' ')
    text = ' '.join(text.split())  # Normalize multiple spaces to a single space
    return text