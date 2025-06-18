from bs4 import BeautifulSoup
import pandas as pd
import requests
    
def has_books_from_series_heading(soup):
    return any(h2.text.strip() == 'Books from the series' for h2 in soup.find_all('h2'))

def get_series_name(url):
    try:
        page = requests.get(url) 
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            if has_books_from_series_heading(soup):
                for a in soup.find_all('a', href=True):
                    if '/series/' in a['href'] and a.text.strip() != 'SERIES':
                        print(url, a.text.strip())
                        return a.text.strip()
    except: print('Invalid URL')                
    return None

albatrosmedia = pd.read_excel('excel tables/Scraped Data AlbatrosMedia.xlsx', nrows = 601)
albatrosmedia['Scraped Series'] = albatrosmedia['URL'].apply(lambda x: get_series_name(x))
albatrosmedia.to_excel('excel tables/Scraped Data AlbatrosMedia Series.xlsx')

