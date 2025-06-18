import os
from pypdf import PdfReader
from readability import Readability
import pandas as pd
from textstat import textstat
from lexicalrichness import LexicalRichness

def remove_headings(text):
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        if len(line.split()) > 4:
            cleaned_lines.append(line)
    return " ".join(cleaned_lines)


def count_readability(filename, text, readability_dict):
    text = remove_headings(text)    
    if len(text.split())>100:
        lex = LexicalRichness(text)
        readability_dict['Book Name'].append(filename)
        readability_dict['Readability Flesch score'].append(textstat.flesch_reading_ease(text))
        readability_dict['Readability Gunning Fog score'].append(textstat.gunning_fog(text))
        readability_dict['Difficult words'].append(textstat.difficult_words(text))
        readability_dict['Tokens'].append(len(text.split()))
        readability_dict['Type-Token'].append(lex.ttr)
        print(textstat.flesch_reading_ease(text))
        print(textstat.gunning_fog(text))
    else:
        readability_dict['Book Name'].append(filename)
        readability_dict['Readability Flesch score'].append(None)
        readability_dict['Readability Gunning Fog score'].append(None)
        readability_dict['Difficult words'].append(None)
        readability_dict['Tokens'].append(len(text.split()))
        readability_dict['Type-Token'].append(None)
        print('Not enough text') 
    return readability_dict    


def save_text(directory):
    readability_dict = {'Book Name': [], 'Readability Flesch score': [], 'Readability Gunning Fog score': [], 'Difficult words': [], 'Tokens': [], 'Type-Token': []}
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename != '.DS_Store':
                file = os.path.join(dirpath, filename)
                print(filename) 
                try: 
                    reader = PdfReader(file)
                    print(len(reader.pages))
                    readability_dict['Pages'].append(len(reader.pages))
                    text = '\n'.join([reader.pages[x].extract_text() for x in range(len(reader.pages))])
                    filename = filename[:-4]
                    #with open(f'Plain text/{filename}.txt', 'w') as output:
                    #    output.write(text)
                    readability_dict = count_readability(filename, text, readability_dict)  
                except: print('Failed')
    return readability_dict   


def get_readability(directory):
    readability_dict = {'Book Name': [], 'Readability Flesch score': [], 'Readability Gunning Fog score': [], 'Difficult words': [], 'Tokens': [], 'Type-Token': []}
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename != '.DS_Store':
                file = os.path.join(dirpath, filename)
                print(filename) 
                try: 
                    f = open(file, "r")
                    text = f.read()
                    filename = filename[:-4]
                    readability_dict = count_readability(filename, text, readability_dict)    
                    
                except: print('Failed')
    return readability_dict            
if __name__ == '__main__':
    #readability = save_text('PDFs') 
    readability = get_readability('Plain text')
    readability_df = pd.DataFrame(readability)
    readability_df.to_excel('excel tables/Readability scores plain.xlsx')
    readability_df = pd.read_excel('excel tables/Readability scores plain.xlsx')
    podklady_albatros = pd.read_excel('excel tables/podklady Albatros CRM.xlsx', sheet_name = 'knihy detail')
    joined_df = podklady_albatros.merge(readability_df, left_on=['Book Name'], right_on=['Book Name'], suffixes=(False, False))
    print(sum([r not in list(podklady_albatros['Book Name'])  for r in list(readability_df['Book Name'])]))
    print(list(filter(lambda x: x not in list(podklady_albatros['Book Name']), readability_df['Book Name'])))
    joined_df.to_excel('excel tables/Readability scores.xlsx')
                  




