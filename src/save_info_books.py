import pandas as pd
import os
from bs4 import BeautifulSoup
import re
from collections import defaultdict

# strings that should be ommited when scraping descriptions
do_not_use = ['Written by', 'Illustrated by', 'Please fill in your contact details so that we can arrange the delivery of the sample copy for you.', 'Book parameters:']

def filter_description(text):
    return all([d not in text for d in do_not_use])



def parse_html_file(file, info_dict):    
    with open(file, 'rb') as f:

        soup = BeautifulSoup(f.read(),  'html.parser')

        # Get title 
        title = soup.find('h1', class_='title-on-desktop').get_text(strip=True)

        # Find the <link> tag with rel="canonical"
        canonical_link = soup.find("link", rel="canonical")

        # Extract the href attribute
        url = canonical_link["href"] if canonical_link else "Not found"
        
        # Extract writers (handling multiple)
        writer_links = soup.find("p").find_all("a", href=lambda href: "/writer/" in href)
        writers = ";".join([writer.text for writer in writer_links])

        # Extract illustrators (handling multiple)
        illustrator_links = soup.find("p").find_all("a", href=lambda href: "/illustrator/" in href)
        illustrators = ";".join([illustrator.text for illustrator in illustrator_links])

        # Extract age range
        age = soup.find("p").find("strong").text

        #Extract description
        try: description = soup.find_all(class_ = 'perex')[2].find('p').text 
        except: description = 'Not found'
        
        #Extract parameters text
        parameters = soup.find_all("p")[1].text
        
        # Use regex to extract "Book parameters" and "Sold to" separately
        match = re.search(r'Book parameters:(.*?)(?:Sold to:(.*))?$', parameters)

        # Extract the matched text
        book_parameters = match.group(1).strip() if match.group(1) else "Not found"
        sold_to = match.group(2).strip() if match.group(2) else "Not found"

        p_tag = [x.text for x in soup.find_all("p")[2:]]
        description = '\n'.join(set(filter(filter_description, p_tag)))


        info_dict['title'].append(title)
        info_dict['url'].append(url)
        info_dict['writers'].append(writers)
        info_dict['illustrators'].append(illustrators)
        info_dict['ages'].append(age)
        info_dict['book parametes'].append(book_parameters)
        info_dict['sold to'].append(sold_to)
        info_dict['description'].append(description) 
        
        # Print the extracted data
        print(f'URLS: {url}')
        print(f"Writer(s): {writers}")
        print(f"Illustrator(s): {illustrators}")
        print(f"Ages: {age}")
        print(f"Book Parameters: {book_parameters}")
        print(f"Sold To: {sold_to}")
        print(f"Description: {description}")
        return info_dict

podklady_albatros = pd.read_excel('excel tables/podklady Albatros CRM.xlsx', sheet_name = 'knihy detail')
directory = 'html'
info_dict = defaultdict(list)
for dirpath, dirnames, filenames in os.walk(directory):
    for filename in filenames:
        if filename != '.DS_Store':
            category = dirpath[5:]
            info_dict['category'].append(category)
            print(f"Title: {filename}")
            print(f"Category: {category}")
            info_dict = parse_html_file(os.path.join(dirpath, filename), info_dict)
scraped_data = pd.DataFrame(info_dict)  

scraped_data = scraped_data.groupby(['url'], as_index=False).agg({
    'category': list,  # Get all categories as a list
    'url': 'first',  # Get the first URL for each Book Name
    'illustrators': 'first',  # Get the first illustrator for each Book Name
    'ages': 'first',  # Get unique ages for each Book Name
    'book parametes':'first', 
    'sold to': 'first', 
    'description': 'first',
    'title': 'first',
    'writers': 'first'
})

scraped_data.to_excel('excel tables/Scraped Data categories.xlsx')     

joind_df = podklady_albatros.merge(scraped_data, left_on=['Book Name', 'Author'], right_on=['title', 'writers'], suffixes=(False, False))

# collapsed_df = joind_df.groupby('Book Name', as_index=False).agg({
#     'category': 'first',  # Get all categories as a list
#     'Author': 'first',  # Get the first Author for each Book Name
#     'Series: Series Name': 'first',  # Get the first Series Name for each Book Name
#     'Series': 'first',  # Get the first Series for each Book Name
#     'PDF URL': 'first',  # Get the first PDF URL for each Book Name
#     'Picture URL': 'first',  # Get the first Picture URL for each Book Name
#     'YouTube URL': 'first',  # Get the first YouTube URL for each Book Name
#     'Book: Created Date': 'first',  # Get the first Created Date for each Book Name
#     'url': 'first',  # Get the first URL for each Book Name
#     'illustrators': 'first',  # Get the first illustrator for each Book Name
#     'ages': 'first',  # Get unique ages for each Book Name
#     'book parametes':'first', 
#     'sold to': 'first', 
#     'description': 'first'
# })

# joind_df  = joind_df .rename(columns={'url': "Albatros URL", 'illustrators': "Illustrators", 'ages': "Ages", 'book parametes': 'Book parameters', 'sold to': 'Sold to', 'description': 'Description'})
# joind_df.to_excel('Albatros scraping all.xlsx', index=False)



