import gzip
import json
import os.path
import glob
import re






count = 0

oclcs = {}
# this is working with /bibs/OCoLC v2 endpoint reponse
print("Extracting OCLC data")
for file in glob.glob("../data/oclc/*.gz"):
    with gzip.open(file,'rt') as f:
        data = json.loads(f.read())
        oclc_record_id = file.split("/")[-1].split(".")[0]

        if 'type' in data:
            if data['type'] == 'NOT_FOUND':
                print("No OCLC Found", file)
                oclcs[oclc_record_id] = False
                continue


        oclc_data = {
            'record_oclc': oclc_record_id,
            'oclc': None,
            'lcc' : None,
            'date': None,
            'language': None,
            'format':None,
            'work': None,
            'work_count': None,
            'edition_count': None,
            'edition': None,
            'merged_oclc':None,
            'fiction': False,
            'fiction_categories': None,
            'lcsh':None,
        }



        if 'oclc' in data:
            oclc_data['oclc'] = data['oclc']

        if 'identifier' in data:
            if 'oclcNumber' in data['identifier']:
                oclc_data['oclc'] = data['identifier']['oclcNumber']

        if 'editionCluster' in data:
            if 'id' in data['editionCluster']:
                oclc_data['edition'] = data['editionCluster']['id']

        if 'editionCluster' in data:
            if 'count' in data['editionCluster']:
                oclc_data['edition_count'] = data['editionCluster']['count']

        if 'work' in data:
            if 'id' in data['work']:
                oclc_data['work'] = data['work']['id']
        if 'work' in data:
            if 'count' in data['work']:
                oclc_data['work_count'] = data['work']['count']



        if 'classification' in data:
            if 'lc' in data['classification']:
                oclc_data['lcc'] = data['classification']['lc']

        if 'date' in data:
            if 'machineReadableDate' in data['date']:
                oclc_data['date'] = data['date']['machineReadableDate']
        if 'language' in data:
            if 'itemLanguage' in data['language']:
                oclc_data['language'] = data['language']['itemLanguage']
        if 'format' in data:
            if 'generalFormat' in data['format']:
                oclc_data['format'] = data['format']['generalFormat']
        if 'identifier' in data:
            if 'mergedOclcNumbers' in data['identifier']:
                oclc_data['merged_oclc'] = data['identifier']['mergedOclcNumbers']



        if 'format' in data:
            if 'materialTypes' in data['format']:
                if 'fic' in data['format']['materialTypes']:
                    oclc_data['fiction'] = True

        if 'description' in data:
            if 'genres' in data['description']:
                if 'Fiction' in data['description']['genres']:
                    oclc_data['fiction'] = True


        if oclc_data['lcc'] != None:
            if oclc_data['lcc'][0:2] == "PZ":
                oclc_data['fiction'] = True


        if oclc_data['lcc'] != None:
            if oclc_data['lcc'][0:2] == "PR":
                num_search = re.search('PR([0-9]+)', oclc_data['lcc'], re.IGNORECASE)
                if num_search:
                    try:
                        num = int(num_search.group(1))
                    except:
                        num = 0
                    if num > 78:
                        oclc_data['fiction'] = True

        if oclc_data['lcc'] != None:
            if oclc_data['lcc'][0:2] == "PN":
                num_search = re.search('PN([0-9]+)', oclc_data['lcc'], re.IGNORECASE)
                if num_search:
                    try:
                        num = int(num_search.group(1))
                    except:
                        num = 0
                    if num > 5650:
                        oclc_data['fiction'] = True



        if 'subjects' in data:
            for subject in data['subjects']:
                if 'subjectName' in subject:
                    if 'text' in subject['subjectName']:
                        if 'fiction' in subject['subjectName']['text'].lower():

                            if oclc_data['fiction_categories'] == None:
                                oclc_data['fiction_categories']=[]

                            oclc_data['fiction'] = True
                            if subject['subjectName']['text'] not in oclc_data['fiction_categories']:
                                oclc_data['fiction_categories'].append(subject['subjectName']['text'])
                            # print(oclc_record_id, subject['subjectName']['text'])



        if 'subjects' in data:
            for subject in data['subjects']:
                if 'vocabulary' in subject:
                    if subject['vocabulary'] == 'Library of Congress Subject Headings':
                        if oclc_data['lcsh'] == None:
                            oclc_data['lcsh'] = []

                        oclc_data['lcsh'].append(subject['subjectName']['text'])


        if oclc_data['fiction'] == True:
            # print(oclc_data['fiction_categories'])

            if oclc_data['fiction_categories'] != None:
                for s in oclc_data['fiction_categories']:
                    if 'history and criticism' in s.lower():
                        oclc_data['fiction'] = False
                        oclc_data['fiction_categories'] = None

            if oclc_data['lcsh'] != None:
                for s in oclc_data['lcsh']:



                    if 'history and criticism' in s.lower():
                        oclc_data['fiction'] = False
                        oclc_data['fiction_categories'] = None


                    if 'literature anecdotes' in s.lower():
                        oclc_data['fiction'] = False
                        oclc_data['fiction_categories'] = None








        # print(oclc_data['fiction_categories'])
        # if oclc_data['fiction'] == True:
        #     count=count+1
        #     print(count)

        # if 'fiction' in json.dumps(data).lower() and oclc_data['fiction'] == False:
        #     # print(json.dumps(data,indent=2))
        #     count=count+1
        #     print(count)



        oclcs[oclc_record_id] = oclc_data


print(oclcs['596932'])

recs = {}
print("Merging Collection")
with gzip.open(f'../data/hathi_collection_with_marc_oclc.ndjson.gz', "wb", compresslevel=9) as f_final:

    with gzip.open('../data/hathi_collection_with_marc.ndjson.gz','rt') as f:
        for line in f:
            count=count+1
            data = json.loads(line)
            

            for record_oclc in data['oclc_num'].split(","):
                
                found = False
                if record_oclc in oclcs:
                    if oclcs[record_oclc] != False:
                        found = oclcs[record_oclc]
                        break



            if found != False:
                data['oclc_data'] = found
            else:
                pass


                # do something with the multi OCLC here? data['oclc_num']


            line_out = json.dumps(data) + '\n'
            f_final.write(line_out.encode("utf-8")) 



            

