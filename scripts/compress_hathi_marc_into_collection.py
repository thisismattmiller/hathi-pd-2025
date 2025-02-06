import gzip
import json
import os.path
import glob


count = 0
recs = {}
print("Reading Collection")
with gzip.open('../data/hathi_collection.ndjson.gz','rt') as f:
    for line in f:
        count=count+1
        data = json.loads(line)
        hid = data['ht_bib_key']    
        data['vols'] = []

        if hid in recs:

            if data['description'] != '':                
                # if it has a description keep track of it otherwise it is probably just another scan of the same vol
                recs[hid]['vols'].append({ 'htid': data['htid'], 'desc': data['description'] })

                

        else:

            recs[hid] = data
print(count)
count=0
print("Merging MARC with Collection")
print(len(list(glob.glob("../data/hathi_marc/*.gz"))))
for file in glob.glob("../data/hathi_marc/*.gz"):
    with gzip.open(file,'rt') as f:
        marc = json.loads(f.read())


        hid = file.split("/")[-1].split(".")[0]
        count=count+1
        if hid not in recs:
            print("hid not found",hid)
            continue
            # break

        recs[hid]['marc'] = marc
print(count)

print("Writing new Collection")
with gzip.open(f'../data/hathi_collection_with_marc.ndjson.gz', "wb", compresslevel=9) as f:
    
    for hid in recs:

        line = json.dumps(recs[hid]) + '\n'
        f.write(line.encode("utf-8")) 



        

