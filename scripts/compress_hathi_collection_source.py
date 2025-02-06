import json

# from https://babel.hathitrust.org/cgi/ls?a=srchls;c=1979856759;q1=*
# this is just compressing it down to a new line delimted json file so we can
# gzip it and keep it in the repo

data = json.load(open("/Users/m/Downloads/1979856759-1738712329.json"))
with open("../data/hathi_collection.ndjson",'w')as file:
	for book in data['gathers']:
		file.write(json.dumps(book) +'\n')