import gzip
import json
import requests
import os.path


count = 0
with gzip.open('../data/hathi_collection.ndjson.gz','rt') as f:
    for line in f:
        count=count+1

        # !!!!!!
        # if count < 50000:
        #     continue

        data = json.loads(line)

        url = f"https://babel.hathitrust.org/cgi/pt?id={data['htid']}"
        hid = data['ht_bib_key']

        if os.path.isfile(f'../data/hathi_web/{hid}.json.gz') == True:
            continue

        print(count, url)

        try:
            rep = requests.get(url)

        except KeyboardInterrupt:
            xxxxx=x
        except:
            print("Network Error on this one")
            print(line)
            continue

        lines = rep.text.split("\n")


        script_goblin_mode = False
        web_data = {}

        for line in lines:
            
            if '</script>' in line:
                break

            if 'HT = HT' in line:
                continue


            if script_goblin_mode == True:


                line = line.strip()
                if len(line) > 0:

                    if line[-1] == ';':
                        line = line[0:-1]


                    if ' = {' in line:
                        line = line.replace(" = {", '<SPLIT>{')
                        pair = line.split('<SPLIT>')

                    elif 'sectionList = [' in line:
                        line = line.replace("sectionList = [", 'sectionList <SPLIT> [')
                        pair = line.split('<SPLIT>')
                    elif 'externalLinks = [' in line:
                        line = line.replace("externalLinks = [", 'externalLinks <SPLIT> [')
                        pair = line.split('<SPLIT>')

                    else:
                        pair = line.split("=")
                    

                    if len(pair) != 2:
                        print("Error on this one", url)
                        print("line:")
                        print(line)
                        xxxxxx=xx

                    var = pair[0]
                    val = pair[1]
                    val = val.strip()

                    if val[0] == "'":
                        val = '"' + val[1:-1]  +'"' 

                    val = json.loads(val)
                    web_data[var] = val



            if '<script>' in line:
                script_goblin_mode = True



        # write it out
        with gzip.open(f'../data/hathi_web/{hid}.json.gz', "wb") as f:
            f.write(json.dumps(web_data).encode("utf-8")) 





#        