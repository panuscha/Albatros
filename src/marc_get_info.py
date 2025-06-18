def fix_name(name):
    name = name.strip(' ,')
    spl = name.split(',')
    return f'{spl[1]} {spl[0]}' if len(spl) == 2 else name

def add_ill_aut( function, authority, author, illustrator): 
    if function == 'ill':
        illustrator += ';' + authority
    if function == 'aut':
        author += ';' + authority  
    return illustrator, author            

def get_041(record):
    '''Returns original language and language of text'''
    language_orig = 'cze'
    language_text = 'cze'
    # Get Language from 041
    for field in record.get_fields('041'):
        for subfield in field.get_subfields('a'):   
            language_text = subfield  
        for subfield in field.get_subfields('h'):   
            language_orig = subfield
    return language_orig, language_text        
              
def get_author_illustrator(record):  
    '''Returns Author and Illustrator from 100 and 700 '''  
    illustrator = ''
    author = ''

    # Get Author from 100
    for field in record.get_fields('100'):
        subfields = field.subfields_as_dict()
        authority = fix_name(subfields['a'][0])
        for function in subfields['4']:
            illustrator, author  = add_ill_aut(function, authority, author, illustrator)  
    # Get info from 700   
    for field in record.get_fields('700'):
        subfields = field.subfields_as_dict()
        if '4' in subfields.keys() and len(subfields['a']) == len(subfields['4']):  
            for authority, function in zip(subfields['a'], subfields['4'] ):
                authority = fix_name(authority)
                illustrator, author  = add_ill_aut(function, authority, author, illustrator)          
    return author.strip(' ;'), illustrator.strip(' ;')        
        
def get_title(record): 
    '''Returns Title from 245''' 
    title = None        
    # Get Title    
    for field in record.get_fields('245'):
        for subfield in field.get_subfields('a'):   
            title = subfield.strip(' ,:/') 
            title = 'Seasons (Learning Wheel)' if title == 'Seasons' else title 
            title = 'Little Red Riding Hood (FT Shape Books)' if title == 'Little Red Riding Hood' else title  
            break
    return title   

def get_original_title(record): 
    '''Returns Original Title from 240''' 
    title = None        
    # Get Title    
    for field in record.get_fields('240'):
        for subfield in field.get_subfields('a'):   
            title = subfield.strip(' ,:/') 
            title = 'Seasons (Learning Wheel)' if title == 'Seasons' else title 
            title = 'Little Red Riding Hood (FT Shape Books)' if title == 'Little Red Riding Hood' else title  
            break
    return title   
  
def get_year_page(record):
    '''Returns year and pages''' 
    year = None
    #Get Year
    for field in record.get_fields('264'):
        for subfield in field.get_subfields('c'):   
            year = int(''.join(i for i in subfield if i.isdigit()))      
        
    # Get Pages
    for field in record.get_fields('300'):
        subfields = field.subfields_as_dict()
        if 'a' in subfields.keys():
            pages = int(''.join(i for i in subfields['a'][0] if i.isdigit())) 
    return year, pages        
        
        