import pymarc as pm

def do_it(r): #Literatura pro děti a mládež
    childer_lit = False
    for field in r.get_fields('072'):
       for subfield in field.get_subfields('x'): 
            if 'Literatura pro děti a mládež' in subfield: 
                childer_lit = True
    if childer_lit:             
        for field in r.get_fields('928'):
            for subfield in field.get_subfields('a'): 
                if 'Albatros' in subfield: 
                    print(r)
                    albatros.append(r)
                    break
                  # only executed if the inner loop did NOT break
               

albatros = []
OUT = 'albatros_literatura_vse.mrc'
pm.map_xml(do_it, '/Users/charlottepanuskova/Downloads/skc.xml')

with open(OUT , 'wb') as writer:
    for record in albatros:
        writer.write(record.as_marc())
