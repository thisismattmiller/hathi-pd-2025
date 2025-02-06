import json
import glob
import os

data = json.load(open('../data/browser_data.json'))


for rec in data:


	print(rec)


	
	html = '<html lang="en">><head>'


	
	
	html = html + "</head><body>"

	html = html + f"<h1>{rec['title']} by {rec['author']}</h1>\n"

	html = html + f"<div>Catalog Id: {rec['hid']} Vol Id: {rec['htid']}</div>\n"
	
	if rec["llama_preview"] != None:
		html = html + f'<div>{rec["llama_preview"]}</div>\n'


	html = html + f'<div data-pagefind-filter="language">{rec["language"]}</div>\n'

	if rec['llama_geners'] != None:
		for genres in rec['llama_geners']:
			html = html + f'<div data-pagefind-filter="genres">{genres}</div>\n'


	for lcsh in rec['lcsh']:
		html = html + f'<div data-pagefind-filter="lcsh">{lcsh}</div>\n'



	html = html + f'\n<p data-pagefind-sort="holdings_count">{rec["holdings_count"]}</p>'
	html = html + f'\n<p data-pagefind-sort="author">{rec["author"]}</p>'
	html = html + f'\n<p data-pagefind-sort="title">{rec["title"]}</p>'
	html = html + f'\n<p data-pagefind-sort="scan_count">{rec["scan_count"]}</p>'




	html = html + "\n</body>\n</html>"		

	with open(f'../data/search_pages/pages/{rec["hid"]}.html','w') as outfile:
		outfile.write(html)



