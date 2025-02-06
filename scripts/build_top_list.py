import gzip
import json
import os.path

works_count = {}
top_titles = {}
count=0
with gzip.open('../data/hathi_collection_final_dataset.ndjson.gz','rt') as f:

    for line in f:
        # count=count+1
        data = json.loads(line)
        
        hid = data['ht_bib_key']


        if data['genre_format'] != 'Book':
            continue

        if data['fiction_flag'] == False:
            continue




        if 'oclc_data' in data:

            if data['oclc_data']['work'] not in top_titles:
                top_titles[data['oclc_data']['work']] = data['marc_245_a'] +' ' + data['author'] + " | " + data['handle_url']

            # overwrite eng if comes across
            if data['language'] == 'eng':
                top_titles[data['oclc_data']['work']] = data['marc_245_a'] +' ' + data['author'] + " | " + data['handle_url']
                


            if 'holdings_count' in data:

                if data['oclc_data']['work'] not in works_count:
                    works_count[data['oclc_data']['work']] = 0


                works_count[data['oclc_data']['work']] = works_count[data['oclc_data']['work']] + data['holdings_count'] 









#                 # print(data)
#                 count=count+1
#                 top_titles[data['marc_245_a'] +' ' + data['author'] + " | " + data['handle_url']] = data['holdings_count'] 


top_works_count_sorted = dict(sorted(works_count.items(), key=lambda item: item[1], reverse=True))




for t in top_works_count_sorted:

    print(works_count[t],'--',top_titles[t])



print(count)