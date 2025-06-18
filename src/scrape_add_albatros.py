from bs4 import BeautifulSoup
import requests
import re
import os

def iterate_list(l):
    ret = []
    for category in l:
        title = category.text.strip()  # Get title
        if title != '':
            url = category["href"]  # Get URL    
            print(f"Title: {title}, URL: {url}")
            match = re.search(r'https://www\.albatrosmedia\.eu/book/([^/"\s]+)', url)
            if match:
                result = match.group(1) 
            ret.append((result, url))
    return ret   

def save_urls():
    # ALL URL
    url = 'https://www.albatrosmedia.eu/category/all/'
    page = requests.get(url) 
    if page.status_code == 200:
        Bs_data = BeautifulSoup(page.content, 'html.parser')
        book_list = Bs_data.find_all(href=re.compile("https://www.albatrosmedia.eu/book/"))  
        book_list = list(filter(lambda x: '<a class="book-teaser' not  in str(x) , book_list))    
        iter = iterate_list(book_list)
    return iter

def iterate_categories(books_urls): 
    newpath = f'all/' 
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    for book_title, url in books_urls:
        page = requests.get(url)
        with open(f'{newpath}/{book_title}.html', 'wb+') as f:
            f.write(page.content)

if __name__ == '__main__':
    books_urls = save_urls()
    iterate_categories(books_urls)