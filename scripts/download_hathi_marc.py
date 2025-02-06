import gzip
import json
import requests
import os.path


count = 0
with gzip.open('../data/hathi_collection.ndjson.gz','rt') as f:
    for line in f:
        count=count+1
        data = json.loads(line)
        url = data['catalog_url'] + '.json'

        hid = data['ht_bib_key']

        if os.path.isfile(f'../data/hathi_marc/{hid}.json.gz') == True:
            print('skip', count)
            continue

        print(count, url)

        try:
            rep = requests.get(url)
            rep = rep.json()
        except:
            print("Error on this one")
            print(line)
            break

        # write it out
        with gzip.open(f'../data/hathi_marc/{hid}.json.gz', "wb") as f:
            f.write(json.dumps(rep).encode("utf-8")) 





#        