import json
import requests
import string
import unicodedata
from thefuzz import fuzz

data = json.load(open("../data/lccns_to_check.json"))


def normalize_string(s):
    s = str(s)
    s = s.translate(str.maketrans('', '', string.punctuation))
    s = " ".join(s.split())
    s = s.lower()
    s = s.casefold()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = s.replace('the','')
    return s

for key in data:



	aap = data[key]['author'] + ' ' + data[key]['title']

	resp = requests.get(f'https://id.loc.gov/resources/instances/suggest2/?q={data[key]["lccn"]}&searchtype=keyword')

	jresp = resp.json()

	for hit in jresp['hits']:
		raito = fuzz.ratio(normalize_string(aap), normalize_string(hit['suggestLabel']))
		if raito >= 70:
			print("-----")
			print(hit['suggestLabel'])
			print(aap)
			print(raito)
			work_uri = hit['uri'].replace("/instances/",'/works/')
			print(work_uri)

			work_req = requests.get(work_uri+'.bibframe.json')
			work_json = work_req.json()

			for graph in work_json:
				for p in graph:
					if p=='http://id.loc.gov/ontologies/bibframe/classificationPortion':
						if graph['@type'][0] == "http://id.loc.gov/ontologies/bibframe/ClassificationLcc":
							data[key]['lcc'] = graph[p][0]['@value']

							print(data[key])
							json.dump(data,open("../data/lccns_checked.json",'w'))
