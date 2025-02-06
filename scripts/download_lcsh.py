import json
import requests
import string
import time
import unicodedata
from thefuzz import fuzz

data = None
try:
	data = json.load(open("../data/lcsh_checked.json"))
except:
	data = json.load(open("../data/lcsh_to_check.json"))


def normalize_string(s):
    s = str(s)
    s = s.translate(str.maketrans('', '', string.punctuation))
    s = " ".join(s.split())
    s = s.lower()
    s = s.casefold()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = s.replace('the','')
    return s

count = 0
for key in data:
	count=count+1
	print(count, key)

	if data[key] == "done":
		continue

	print(f'https://id.loc.gov/authorities/subjects/suggest2/?q={key}&searchtype=keyword')
	try:
		resp = requests.get(f'https://id.loc.gov/authorities/subjects/suggest2/?q={key}&searchtype=keyword')
	except:
		time.sleep(30)
		resp = requests.get(f'https://id.loc.gov/authorities/subjects/suggest2/?q={key}&searchtype=keyword')


	try:
		jresp = resp.json()
	except:
		print("BAD JSON!!!")
		continue

	
	found_lcc = False
	for hit in jresp['hits']:
		if found_lcc== True:
			break

		## oclc removes the -- ....:(
		hit['suggestLabel'] = hit['suggestLabel'].replace('--',' ')
		raito = fuzz.ratio(normalize_string(key), normalize_string(hit['suggestLabel']))
		if raito >= 95:
			# print("-----")
			# print(hit['suggestLabel'])
			# print(key)
			# print(raito)
			# print(normalize_string(key), normalize_string(hit['suggestLabel']))
			lcsh_uri = hit['uri']
			# print(lcsh_uri)

			found_lcc= True
			try:
				lcsh_req = requests.get(lcsh_uri+'.json')
			except:
				print("Time out")
				time.sleep(30)
				lcsh_req = requests.get(lcsh_uri+'.json')
				
			lcsh_json = lcsh_req.json()

			for graph in lcsh_json:
				if '@type' in graph:
					if "http://id.loc.gov/ontologies/lcc#ClassNumber" in graph['@type']:

						lcc = graph['http://www.loc.gov/mads/rdf/v1#code'][0]['@value']
						lcc = lcc.split("-")[0]
						print(key,'==',lcc)
						
						data[key] = lcc
						json.dump(data,open("../data/lcsh_checked.json",'w'))


						break

	
