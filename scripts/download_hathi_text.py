import gzip
import json
import requests
import os.path
from bs4 import BeautifulSoup

count = 0
with gzip.open('../data/hathi_collection_final_dataset.ndjson.gz','rt') as f:
    for line in f:
        count=count+1

        # !!!!!!
        # if count < 50000:
        #     continue

        data = json.loads(line)


        if data['fiction_flag'] != True:
            continue

        
        ht_bib_key = data['ht_bib_key']





        web_data=gzip.open(f'../data/hathi_web/{ht_bib_key}.json.gz','rb')
        web_data_content=web_data.read()
        web_data = json.loads(web_data_content)

        # print(json.dumps(web_data,indent=2))
        # 
        section_seq = []
        if 'HT.params.sectionList ' in web_data:
            # print(json.dumps(web_data['HT.params.sectionList '],indent=2))
            for seg in web_data['HT.params.sectionList ']:
                if 'Section' in seg['label']:
                    section_seq.append(seg['seq'])

            if len(section_seq) == 0:
                section_seq.append(0)
            # print(json.dumps(web_data['HT.params.sectionList '],indent=2))
            # print(section_seq)


            # if len(section_seq) > 0:
            #     if section_seq[0]

            # else:
        else:
            # no section list means no ocr
            # print(json.dumps(web_data,indent=2))
            continue

        start = 0
        end = 50
        if len(web_data['HT.params.sectionList ']) > 0:   

            start = int(section_seq[0])
            end = start+50
            total = web_data['HT.params.totalSeq ']
            if int(section_seq[0]) + 50 > total:
                start = 1

            if start + 50 > total:
                end = total
        elif 'HT.params.featureList ' in web_data:
            if len(web_data['HT.params.featureList ']) > 0:
                start = 0 
                if len(web_data['HT.params.featureList ']) < 50:
                    end = len(web_data['HT.params.featureList '])
                else:
                    end = 50
            else:
                continue


        if start/end*100 > 50:
            start=1
            if end <= 50:
                end = end
            else:
                end = 50

        
        if os.path.isfile('../data/hathi_text/'+ht_bib_key+'.json') == True:
            print(start,end, 'skipp')
            continue

        print(start,end)

        if end-start > 51:
            end = start + 50
            

        all_text=[]

        for x in range(start,end+1):
            url = f'https://babel.hathitrust.org/cgi/ssd?id={data["htid"]};page=ssd;view=plaintext;seq={x};'
            print("\t",x,'/',end+1,url)

            req = requests.get(url)
            html = req.text


            soup = BeautifulSoup(html, 'html.parser')
            text_el = soup.find(attrs={'class':"Text"})
            if text_el != None:
                all_text.append(text_el.text)
            else:
                print("No text")

            json.dump(all_text,open('../data/hathi_text/'+ht_bib_key+'.json','w'))


        # url = f"https://babel.hathitrust.org/cgi/pt?id={data['htid']}"
        # hid = data['ht_bib_key']

        # if os.path.isfile(f'../data/hathi_web/{hid}.json.gz') == True:
        #     continue

        # print(count, url)

        # try:
        #     rep = requests.get(url)

        # except KeyboardInterrupt:
        #     xxxxx=x
        # except:
        #     print("Network Error on this one")
        #     print(line)
        #     continue

        # lines = rep.text.split("\n")


        # script_goblin_mode = False
        # web_data = {}

        # for line in lines:
            
        #     if '</script>' in line:
        #         break

        #     if 'HT = HT' in line:
        #         continue


        #     if script_goblin_mode == True:


        #         line = line.strip()
        #         if len(line) > 0:

        #             if line[-1] == ';':
        #                 line = line[0:-1]


        #             if ' = {' in line:
        #                 line = line.replace(" = {", '<SPLIT>{')
        #                 pair = line.split('<SPLIT>')

        #             elif 'sectionList = [' in line:
        #                 line = line.replace("sectionList = [", 'sectionList <SPLIT> [')
        #                 pair = line.split('<SPLIT>')
        #             elif 'externalLinks = [' in line:
        #                 line = line.replace("externalLinks = [", 'externalLinks <SPLIT> [')
        #                 pair = line.split('<SPLIT>')

        #             else:
        #                 pair = line.split("=")
                    

        #             if len(pair) != 2:
        #                 print("Error on this one", url)
        #                 print("line:")
        #                 print(line)
        #                 xxxxxx=xx

        #             var = pair[0]
        #             val = pair[1]
        #             val = val.strip()

        #             if val[0] == "'":
        #                 val = '"' + val[1:-1]  +'"' 

        #             val = json.loads(val)
        #             web_data[var] = val



        #     if '<script>' in line:
        #         script_goblin_mode = True



        # # write it out
        # with gzip.open(f'../data/hathi_web/{hid}.json.gz', "wb") as f:
        #     f.write(json.dumps(web_data).encode("utf-8")) 





#        