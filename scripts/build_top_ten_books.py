import json
import os.path
import string
import string 
import unicodedata




def normalize_string(s):
    s = str(s)
    s = s.translate(str.maketrans('', '', string.punctuation))
    s = " ".join(s.split())
    s = s.lower()
    s = s.casefold()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = s.replace('the','')
    return s



data = json.load(open('../data/browser_data.json'))


llm_cat = {}
lcsh_cat = {}

for b in data:

    for lcsh in b['lcsh']:
        
        lcsh_normalized = normalize_string(lcsh)

        if lcsh_normalized not in lcsh_cat:
            lcsh_cat[lcsh_normalized] = {'lcsh':lcsh,'count':0}

        lcsh_cat[lcsh_normalized]['count']=lcsh_cat[lcsh_normalized]['count']+1

    if b['llama_geners'] != None:
        for llm in b['llama_geners']:
            
            llm_normalized = normalize_string(llm)

            if llm_normalized not in llm_cat:
                llm_cat[llm_normalized] = {'llm':llm,'count':0}

            llm_cat[llm_normalized]['count']=llm_cat[llm_normalized]['count']+1



llm_cat_list = []
for llm in llm_cat:
    llm_cat_list.append(llm_cat[llm])


llm_cat_sorted = sorted(llm_cat_list, key=lambda d: d['count'], reverse=True)




lcsh_cat_list = []
for lcsh in lcsh_cat:
    lcsh_cat_list.append(lcsh_cat[lcsh])


lcsh_cat_sorted = sorted(lcsh_cat_list, key=lambda d: d['count'], reverse=True)
print(llm_cat_sorted)

# json.dump(final_vols,open('../data/browser_data.json','w'))

