import requests
import json
import os
import time
import gzip


auth_timestamp = None
headers = {}

def reauth():
    global auth_timestamp
    global headers
    print(os.environ['OCLC_CLIENT_ID'])
    response = requests.post(
        'https://oauth.oclc.org/token',
        data={"grant_type": "client_credentials", 'scope': ['wcapi']},
        auth=(os.environ['OCLC_CLIENT_ID'], os.environ['OCLC_SECRET']),
    )
    print(response.text)
    token = response.json()["access_token"]
    auth_timestamp = time.time()

    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }


reauth()

count=0

with gzip.open('../data/hathi_collection_with_marc_oclc.ndjson.gz','rt') as f:
    for line in f:
        sec_left = time.time() - auth_timestamp
        sec_left = 1199 - 1 - int(sec_left)

        if sec_left < 10:
            print("Bearer is about to expire, reauthing...")
            reauth()


        count=count+1
        data = json.loads(line)

        oclc = data['oclc_num']

        for oclc in oclc.split(','):

            oclc=oclc.strip()

            if oclc != '':


                if os.path.isfile(f'../data/holdings/{oclc}.json.gz') == True:
                    continue


                print(count, f"({sec_left})",oclc)
                url = f'https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs-summary-holdings'
                params={
                    'oclcNumber': oclc
                }

                
                reponse_text = ""
                try:
                    response = requests.get(url,headers=headers,params=params)
                    reponse_text = response.text
                    data = response.json()
                except Exception as e: 

                    if 'Read timed out' in str(e):
                        print("Read timed out, sleeping")
                        time.sleep(5)

                        try:
                            response = requests.get(url,headers=headers,params=params)
                            reponse_text = response.text
                            data = response.json()
                        except Exception as e: 

                            print("Error on this one")
                            print(line)
                            print(reponse_text)
                            print(e)
                            break
                # write it out
                with gzip.open(f'../data/holdings/{oclc}.json.gz', "wb") as f:
                    f.write(json.dumps(data).encode("utf-8")) 



