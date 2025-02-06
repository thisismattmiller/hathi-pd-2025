import gzip
import json
import os.path
import string


works_count = {}
top_titles = {}
count=0
with gzip.open('../data/hathi_collection_final_dataset.ndjson.gz','rt') as f:

    for line in f:

        count=count+1
        data = json.loads(line)        
        
        if data['genre_format'] not in works_count:
            works_count[data['genre_format']] = 0


        works_count[data['genre_format']]=works_count[data['genre_format']]+1


print(count)
print(works_count)

for k in works_count:

    print(k, works_count[k] / count * 100)