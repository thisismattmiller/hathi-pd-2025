import gzip
import json
import os.path
import string


works_count = {}
top_titles = {}
has_lcc = 0
got_lcc = 0

has_lcsh = 0
got_lcsh = 0

count=0
with gzip.open('../data/hathi_collection_final_dataset.ndjson.gz','rt') as f:

    for line in f:

        count=count+1
        data = json.loads(line)        
        
        if data['genre_format'] not in works_count:
            works_count[data['genre_format']] = 0


        works_count[data['genre_format']]=works_count[data['genre_format']]+1

        counted_lcsh = False
        for field in data['marc']['fields']:
            if '050' in field:
                has_lcc=has_lcc+1
            if '650' in field and counted_lcsh == False:
                has_lcsh=has_lcsh+1
                counted_lcsh=True

        if data['lcc'] != None and data['lcc'] != False:
            got_lcc = got_lcc+1

        if 'oclc_data' in data:
            got_lcsh=got_lcsh+1


print(count)
print(works_count)

for k in works_count:

    print(k, works_count[k] / count * 100)


print("has_lcc",has_lcc, has_lcc/count * 100)
print("got_lcc",got_lcc, got_lcc/count * 100)

print("has_lcsh",has_lcsh, has_lcsh/count * 100)
print("got_lcsh",got_lcsh, got_lcsh/count * 100)




