import pandas as pd
import os
from bs4 import BeautifulSoup
import re
import requests
import re

def save_PDF(row):
    url = row['PDF URL'] 
    match = re.match(r'^(\S+)', url)
    if match:
        url = match.group(1)
    title = row['Book Name']
    print(title)
    if not pd.isnull(url):
        try:
            response = requests.get(url)
            file_Path = f'PDFs/{title}.pdf'
            if response.status_code == 200:
                with open(file_Path, 'wb') as file:
                    file.write(response.content)
        except: 
            print(f'Invalid URL: {url}')  

if __name__ == '__main__':              
    path = 'excel tables/podklady Albatros CRM.xlsx'
    df = pd.read_excel(path, sheet_name = 'knihy detail')
    filenames_striped = []
    for dirpath, _, filenames in os.walk('PDFs'):
        filenames_striped.extend([filename[:-4] for filename in filenames])
    df = df[~df['Book Name'].isin(filenames_striped)]
    df = df[~df['PDF URL'].isna()]
    df[['Book Name', 'PDF URL']].apply(save_PDF, axis = 'columns')

    

