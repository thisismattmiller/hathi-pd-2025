import json



def process_level(levelObj):

	value = 0 

	if 'value' in levelObj:
		print(levelObj['value'])
		value = value + levelObj['value']

	if 'children' in levelObj:
		if len(levelObj['children']) > 0:
			for child in levelObj['children']:
				value = value + process_level(child)
	
	if 'hash' in levelObj:

		levelObj['count'] = value

	return value




existing_hierarchy = json.load(open('../data/lcc_hiearchy_1929_pd.json'))


v = process_level(existing_hierarchy)
json.dump(existing_hierarchy,open('../data/lcc_hiearchy_1929_pd.json','w'))

