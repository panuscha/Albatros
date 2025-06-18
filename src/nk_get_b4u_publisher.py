import pymarc as pm

def do_it(r):
    for field in r.get_fields('928'):
       for subfield in field.get_subfields('a'): 
            if subfield in ['B4U Publishing', 'Albatros Media - B4U Publishing']: 
                print(r)
                b4u.append(r)
                break
            else:
                continue  # only executed if the inner loop did NOT break
            break    

b4u = []
OUT = 'b4u.marc'
pm.map_xml(do_it, '/Users/charlottepanuskova/Downloads/skc.xml')

with open(OUT , 'wb') as writer:
    for record in b4u:
        writer.write(record.as_marc())
