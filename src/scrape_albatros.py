from bs4 import BeautifulSoup
import requests
import re
import os

def iterate_list(l):
    ret = []
    for category in l:
        title = category.text.strip()  # Get category title
        url = category["href"]  # Get category URL    
        print(f"Title: {title}, URL: {url}")
        ret.append((title , url))
    return ret   

def iterate_list_books(l):
    ret = []
    for category in l:
        title = category.text.strip()  # Get category title
        url = category["href"]  # Get category URL    
        print(f"Title: {title}, URL: {url}")
        match = re.search(r'https://www\.albatrosmedia\.eu/book/([^/"\s]+)', url)
        if match:
            result = match.group(1) 
        ret.append((result, url))
    return ret   

def save_urls():
    # ALL URL
    url = 'https://www.albatrosmedia.eu/category/all/'
    #url = 'https://www.albatrosbooks.com/category/all-2/'
    page = requests.get(url) 
    category_titles = {}
    if page.status_code == 200:
        Bs_data = BeautifulSoup(page.content, 'html.parser')
        age_groups = Bs_data.find_all(href=re.compile("https://www.albatrosmedia.eu/category/all/")) 
        taxonomy = Bs_data.find_all(href=re.compile("https://www.albatrosmedia.eu/category/")) 
        #age_groups = Bs_data.find_all(href=re.compile('https://www.albatrosbooks.com/category/all-2/')) 
        #taxonomy = Bs_data.find_all(href=re.compile('https://www.albatrosbooks.com/category/')) 
        taxonomy = list(filter(lambda x: x not in age_groups, taxonomy)) 
        iter = iterate_list(taxonomy)
        for (category, url) in iter: 
            page = requests.get(url) 
            if page.status_code == 200:
                Bs_data = BeautifulSoup(page.content, 'html.parser')
                book_links = Bs_data.find_all("a", class_="book-title")
                category_titles[(category, url)] = iterate_list_books(book_links) 
    return category_titles  

def iterate_categories(category_titles):
    for key, value in category_titles.items():
        newpath = f'html/{key[0]}' 
        if not os.path.exists(newpath):
            os.makedirs(newpath)
            for book_title, url in value:
                page = requests.get(url)
                with open(f'{newpath}/{book_title}.html', 'wb+') as f:
                    f.write(page.content)

if __name__ == '__main__':
    category_titles = save_urls()
    iterate_categories(category_titles)