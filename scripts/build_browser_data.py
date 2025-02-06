import gzip
import json
import os.path
import string


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
            if data['oclc_data']['work'] not in works_count:
                works_count[data['oclc_data']['work']] = []
            
            works_count[data['oclc_data']['work']].append({'hid': hid,'lang': data['language'], 'size': len(json.dumps(data)), 'record':data })

        # if 'oclc_data' in data:

        #     if data['oclc_data']['work'] not in top_titles:
        #         top_titles[data['oclc_data']['work']] = data['marc_245_a'] +' ' + data['author'] + " | " + data['handle_url']

        #     # overwrite eng if comes across
        #     if data['language'] == 'eng':
        #         top_titles[data['oclc_data']['work']] = data['marc_245_a'] +' ' + data['author'] + " | " + data['handle_url']
                


        #     if 'holdings_count' in data:

        #         if data['oclc_data']['work'] not in works_count:
        #             works_count[data['oclc_data']['work']] = 0


        #         works_count[data['oclc_data']['work']] = works_count[data['oclc_data']['work']] + data['holdings_count'] 
multi_works = {}
for w in works_count:

    if len(works_count[w]) > 1:

        works_sorted = sorted(works_count[w], key=lambda d: d['size'], reverse=True)

        first_eng = None
        others = []
        for a_work in works_sorted:
            if a_work['lang'] == 'eng' and first_eng == None:
                first_eng = a_work
            else:
                others.append(a_work)


        if first_eng == None:
            first_eng = others[0]
            others = others[1:]


        multi_works[w] = {'main': first_eng, 'others': others }


final_vols = []

with gzip.open('../data/hathi_collection_final_dataset.ndjson.gz','rt') as f:

    for line in f:
        # count=count+1
        data = json.loads(line)   

        hid = data['ht_bib_key']
        if data['genre_format'] != 'Book':
            continue
        if data['fiction_flag'] == False:
            continue

        if 'holdings_count' not in data:
            data['holdings_count'] = 0

        vol = {
            'hid' : hid,
            'htid': data['cover_id'],
            'language': data['language_name'],
            'title': data['marc_245_a'],
            'author': data['author'],
            'holdings_count': data['holdings_count'],
            'content_test': data['llama_3.3_content_test'],
            'llama_geners': data['llama_3.3_generes'],
            'llama_preview': data['llama_3.3_preview'],
            'scan_count': data['seq_count'],
            'vols': data['vols'],
            'related_vols': [],
            'gutenberg': data['gutenberg'],
            'lcsh': []

        }



        if 'oclc_data' in data:
            vol['work_count'] = data['oclc_data']['work_count']

            if data['oclc_data']['lcsh'] != None:
                vol['lcsh'] = data['oclc_data']['lcsh']


        else:
            vol['work_count'] = 1



        vol['title'] = vol['title'].strip()
        if vol['title'][-1] in string.punctuation:
            vol['title'] = vol['title'][0:-1].strip()

        vol['author'] = vol['author'].strip()
        if len(vol['author'])>0:
            if vol['author'][-1] in string.punctuation:
                vol['author'] = vol['author'][0:-1].strip()



        # print(vol['holdings_count'], vol['work_count'], data['title'])


        if 'oclc_data' in data:

            # # # we need to figure out if this is the 
            if data['oclc_data']['work'] in multi_works:

                # if this is the main one of the cluster build it otherwise keep going

                if hid == multi_works[data['oclc_data']['work']]['main']['hid']:

                    # print("This is the main one for this cluster", data)
                    # print("BEFORE:",vol)
                    # loop through the others and add them

                    for o in multi_works[data['oclc_data']['work']]['others']:
                        o = o['record']
                        vol['holdings_count'] = vol['holdings_count'] + o['holdings_count']
                        vol['work_count'] = vol['work_count'] + o['oclc_data']['work_count']

                        vol['related_vols'].append({'hid': o['ht_bib_key'], 'htid': o['htid'], 'title': o['title'], 'language': o['language_name']  })
                    # print("AFTER:",vol)
                else:
                    # zero it out as we aren't counting it
                    vol = False

        if vol != False:

            final_vols.append(vol)



json.dump(final_vols,open('../data/browser_data.json','w'))

