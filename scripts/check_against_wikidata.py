import json
from thefuzz import fuzz
import string
import unicodedata
data = json.load(open("/Users/m/Downloads/1979856759-1734969218.json"))


# i just saved the wikidata query from the interface so i I dont have to do it in the code
# SELECT ?item ?itemLabel ?author ?authorLabel ?date

# SELECT ?item ?itemLabel ?author ?authorLabel ?date ?instanceOf ?instanceOfLabel

# WHERE
# {
#   VALUES (?datetime) {("1929-01-01T00:00:00Z"^^xsd:dateTime)}
#   ?item wdt:P31 ?instanceOf.
#   ?item wdt:P577 ?datetime. 
#   ?item wdt:P577 ?date.
#   ?item wdt:P50 ?author.
#   SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],mul,en,fr,pl,ru,en,it,de,fi,nl,cs". }  
# }
# limit 10000

wikidata = json.load(open("../data/wikidata_1929_books.json"))
qids = {}
instance_labels = ["periodical","publication","play","written work","memoir","poetry collection","literary work","musical work/composition","short story collection","dramatic work","reference work","book","wordless novel","serial","doctoral thesis","printed book","graphic novel","creative work","fairy tale","feuilleton","book series","multivolume work","printed work","report","volume","crime novel","collection volume","poetry","review","lyric poetry","narrative poetry","prose poetry","work","fiction literature","travel book","master's thesis","epic poem","scholarly work","translation","serialized fiction","art exhibition","exhibition catalogue","art catalog","biography","pictorial work","treatise","thesis","catalogue raisonné","drama","one-act play","bibliography","auction catalog","lyrics","collection catalog","written or drawn work","digital representation","cross-reference","short story","dissertation","diary","picture book","version, edition or translation"]

for item in wikidata:

	if item['instanceOfLabel'] not in instance_labels:
		continue

	qids[item['item']] = item


wikidata=[]
for k in qids:
	wikidata.append(qids[k])


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
for hathi_record in data['gathers']:


	hathi_title = hathi_record['title']
	hathi_author = hathi_record['author']

	hathi_author_last_name = hathi_record['author'].split(",")[0]

	if hathi_author == '':
		hathi_author=None

	if hathi_author == None:
		continue		

	if ';' in hathi_title:
		hathi_title=hathi_title.split(';')[0]
	if '...' in hathi_title:
		hathi_title=hathi_title.split('...')[0]



	if hathi_author_last_name in hathi_title:

		if ', by' in hathi_title:
			hathi_title=hathi_title.split(', by')[0]

		if '/' in hathi_title:
			hathi_title=hathi_title.split('/')[0]

		if ' by ' in hathi_title:
			hathi_title=hathi_title.split(' by ')[0]
		if ' By ' in hathi_title:
			hathi_title=hathi_title.split(' By ')[0]



	# if hathi_author_last_name in hathi_title:

	# 	print("!!!!",hathi_title)

	# for wiki_item in qids:

	for wiki_item in wikidata:

		title_ratio = fuzz.ratio(normalize_string(wiki_item['itemLabel']), normalize_string(hathi_title))
		# print(normalize_string(wiki_title))
		# print(normalize_string(hathi_title),title_ratio)
		if (title_ratio > 70):
			if normalize_string(hathi_author_last_name) in normalize_string(wiki_item['authorLabel']):
				print(wiki_item['itemLabel'])
				print(hathi_title)
				print(title_ratio)
				print('--------')
				wiki_item['found'] = True





	count=count+1
	if count % 1000 ==0:
		print("------")
		print("------")
		print("------")
		print("------")
		print(count)
		print("------")
		print("------")
		print("------")
		print("------")

		json.dump(wikidata,open('../data/wikidata_1929_books_found.json','w'))
	# for wikititle in wikidata:

	# 	wiki_title = wikititle['itemLabel']
	# 	if 'authorLabel' in wikititle:
	# 		wiki_author = wikititle['authorLabel']
	# 	else:
	# 		wiki_author = None






	# 	# if hathi_author != None and wiki_author != None:



			# data




json.dump(wikidata,open('../data/wikidata_1929_books_found.json','w'))