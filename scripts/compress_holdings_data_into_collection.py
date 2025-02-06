import gzip
import json
import os.path
import glob
import re






count = 0

holdings = {}
# this is working with /bibs/OCoLC v2 endpoint reponse
print("Extracting holdings data")
for file in glob.glob("../data/holdings/*.gz"):
    with gzip.open(file,'rt') as f:
        data = json.loads(f.read())
        oclc_record_id = file.split("/")[-1].split(".")[0]

        if data['numberOfRecords'] == 0:
            print("No OCLC Found", file)
            holdings[oclc_record_id] = False
            continue


        # print(data['briefRecords'][0]['institutionHolding']['totalHoldingCount'])
        oclc_data = {
            'record_oclc': oclc_record_id,
            'count': data['briefRecords'][0]['institutionHolding']['totalHoldingCount']
        }




        holdings[oclc_record_id] = oclc_data



recs = {}
print("Merging Collection")
with gzip.open(f'../data/hathi_collection_with_marc_oclc_holdings.ndjson.gz', "wb", compresslevel=9) as f_final:

    with gzip.open('../data/hathi_collection_with_marc_oclc.ndjson.gz','rt') as f:
        for line in f:
            count=count+1
            data = json.loads(line)


            
            oclc_numbers = data['oclc_num'].split(",")
            if 'oclc_data' in data:
                oclc_numbers.append(data['oclc_data']['record_oclc'])
                oclc_numbers.append(data['oclc_data']['oclc'])

            for record_oclc in oclc_numbers:
                
                found = False
                if record_oclc in holdings:
                    if holdings[record_oclc] != False:
                        found = holdings[record_oclc]
                        break



            if found != False:
                data['holdings_count'] = found['count']
            else:
                pass


            #     # do something with the multi OCLC here? data['oclc_num']


            line_out = json.dumps(data) + '\n'
            f_final.write(line_out.encode("utf-8")) 



            

