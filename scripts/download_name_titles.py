import json
import requests
import string
import time
import unicodedata
from thefuzz import fuzz

data = None
try:
	data = json.load(open("../data/name_titles_checked.json"))
except:
	data = json.load(open("../data/name_titles_to_check.json"))


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
	aap = data[key]['author'] + ' ' + data[key]['title']
	print(count, aap)


	if 'lcc' in data[key]:
		continue 
	if 'checked' in data[key]:
		continue 

	print(f'https://id.loc.gov/resources/works/suggest2/?q={aap}&searchtype=keyword')
	try:
		resp = requests.get(f'https://id.loc.gov/resources/works/suggest2/?q={aap}&searchtype=keyword')
	except:
		time.sleep(30)
		resp = requests.get(f'https://id.loc.gov/resources/works/suggest2/?q={aap}&searchtype=keyword')


	try:
		jresp = resp.json()
	except:
		print("BAD JSON!!!")
		continue

	data[key]['checked'] = True
	found_lcc = False
	for hit in jresp['hits']:
		if found_lcc== True:
			break

		raito = fuzz.ratio(normalize_string(aap), normalize_string(hit['suggestLabel']))
		if raito >= 80:
			print("-----")
			print(hit['suggestLabel'])
			print(aap)
			print(raito)
			work_uri = hit['uri']
			print(work_uri)

			try:
				work_req = requests.get(work_uri+'.bibframe.json')
			except:
				print("Time out")
				time.sleep(30)
				work_req = requests.get(work_uri+'.bibframe.json')
				
			work_json = work_req.json()

			for graph in work_json:
				for p in graph:
					if p=='http://id.loc.gov/ontologies/bibframe/classificationPortion':
						if graph['@type'][0] == "http://id.loc.gov/ontologies/bibframe/ClassificationLcc":
							data[key]['lcc'] = graph[p][0]['@value']
							found_lcc = True
							json.dump(data,open("../data/name_titles_checked.json",'w'))
