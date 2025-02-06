import os
import json
import re
import hashlib
import gzip

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]



hierarchy = {
  'A':{'code':'A', 'subject':'General Works','count':0,'children':{}},
  'B':{'code':'B', 'subject':'Philosophy, Psychology, Religion','count':0,'children':{}},
  'C':{'code':'C', 'subject':'Auxiliary Sciences of History (General)','count':0,'children':{}},
  'D':{'code':'D', 'subject':'World History (except American History)','count':0,'children':{}},
  'E':{'code':'E', 'subject':'American History','count':0,'children':{}},
  'F':{'code':'F', 'subject':'Local History of the United States and British, Dutch, French, and Latin America','count':0,'children':{}},
  'G':{'code':'G', 'subject':'Geography, Anthropology, Recreation','count':0,'children':{}},
  'H':{'code':'H', 'subject':'Social Sciences','count':0,'children':{}},
  'J':{'code':'J', 'subject':'Political Science','count':0,'children':{}},
  'K':{'code':'K', 'subject':'Law','count':0,'children':{}},
  'L':{'code':'L', 'subject':'Education','count':0,'children':{}},
  'M':{'code':'M', 'subject':'Music','count':0,'children':{}},
  'N':{'code':'N', 'subject':'Fine Arts','count':0,'children':{}},
  'P':{'code':'P', 'subject':'Language and Literature','count':0,'children':{}},
  'Q':{'code':'Q', 'subject':'Science','count':0,'children':{}},
  'R':{'code':'R', 'subject':'Medicine','count':0,'children':{}},
  'S':{'code':'S', 'subject':'Agriculture','count':0,'children':{}},
  'T':{'code':'T', 'subject':'Technology','count':0,'children':{}},
  'U':{'code':'U', 'subject':'Military Science','count':0,'children':{}},
  'V':{'code':'V', 'subject':'Naval Science','count':0,'children':{}},
  'Z':{'code':'Z', 'subject':'Bibliography, Library Science','count':0,'children':{}}
}



lcc_f=gzip.open('../data/lcc.json.gz','rb')
lcc_f_content=lcc_f.read()
lcc_data = json.loads(lcc_f_content)
lcc = re.compile(r'([A-Z]+)([0-9]+)')

count = 0
all_data = []

with gzip.open('../data/hathi_collection_final_dataset.ndjson.gz','rt') as f:
	for line in f:

		source_data = json.loads(line)
		htid = source_data['htid']

		cdata = None
		holdings_count = None
		if 'holdings_count' in source_data:
			holdings_count = source_data['holdings_count']
		data = {'id':htid, 'title': source_data['marc_245_a'], 'author':source_data['author'], 'pages':source_data['seq_count'],'lang':source_data['language'],'holdings':holdings_count,'cover':source_data['cover_id']}


		if 'lcc' in source_data:
			if source_data['lcc'] != False:
				if source_data['lcc'] != None:
					data['lcc'] = source_data['lcc']

		data['lccSubject'] = []
		lcc_matches= []

		if 'lcc' in data:
			

			try:
				data['lccSubject'].append(
					{
						'name': hierarchy[data['lcc'][0]]['subject'],
						'code': hierarchy[data['lcc'][0]]['code']
					}
				)
			except:
				print('bad',data)
				continue

			c = data['lcc'].split('.')[0]
			cl = lcc.search(c )
			
			if cl != None:
				
				alpha = cl.group(1)
				num = int(cl.group(2))

				data['lccAlpha'] = alpha
				data['lccNum'] = num


				if alpha in lcc_data:
					for a in lcc_data[alpha]:


						if num >= a['start'] and num <= a['stop']:

							if htid=='coo.31924020560045':
								print(alpha,num)
								print("Match:")
								print(a)
								print(num - a['start'] + a['stop'] - num)
								print("------")

							toadd = a.copy()
							toadd['score'] = num - a['start'] + a['stop'] - num
							lcc_matches.append(toadd)
							# data['lccSubject'].append(
							# 	{
							# 		'name': re.sub(' +', ' ', a['subject']),
							# 		'code': a['id']
							# 	}
							# )

			if len(lcc_matches)>0:

				lowest = 999999999
				lowest_dict = {}
				# print("****",data['lcc'])
				# print(lcc_matches)
				for m in lcc_matches:
					if m['score'] <= lowest:
						lowest_dict = m
						lowest = m['score']

				# we have the top level now add the parents of the winner then the winner

				for p in lowest_dict['parents']:

					for m in lcc_matches:
						if m['id'] == p:
							data['lccSubject'].append(
								{
									'name': re.sub(' +', ' ', m['subject']),
									'code': m['id']
								}
							)					

				data['lccSubject'].append(
					{
						'name': re.sub(' +', ' ', lowest_dict['subject']),
						'code': lowest_dict['id']
					}
				)	

		# if htid=='coo.31924020560045':
		# 	print(lcc_matches)
		# 	print("Wimnnmter")
		# 	print(lowest_dict)
		# 	print(data['lccSubject'])
		# 	xxx=x

		if len(data['lccSubject']) == 0:
			data['lccSubject'].append({
				'name': 'Unknown',
				'code': 'Unknown'
				})
		
		# print(data)
		all_data.append(data)



hiearchyx={
	'name': 'all',
	'children': []
}
largest = 0
hash_data = {}
for d in all_data:

	if 'lccSubject' in d:

		# for s in data['lccSubject']:
		if len(d['lccSubject']) >= largest:
			largest = len(d['lccSubject'])

		hash_str = ""
		hash_lookup = []
		hash_sub_lookup = []
		hash_prehash_lookup = []
		for s in d['lccSubject']:
			hash_str = hash_str + s['name']
			hash_prehash_lookup.append(s['name'])
			hashmd5 = hashlib.md5(hash_str.encode("utf")).hexdigest()
			hash_lookup.append(hashmd5)
			hash_sub_lookup.append(s['name'])
		
			if hashmd5 not in hash_data:
				hash_data[hashmd5] = { 'subject': json.loads(json.dumps(hash_sub_lookup)), 'hash':json.loads(json.dumps(hashmd5)), 'volumes': [] }


			if 'lccAlpha' not in d:
				d['lccAlpha'] = None
			if 'lccNum' not in d:
				d['lccNum'] = None



			hash_data[hashmd5]['volumes'].append({ 'title': d['title'], 'author':d['author'], 'id': d['id'], 'lccA': d['lccAlpha'], 'lccN': d['lccNum'], 'pages':d['pages'],'lang':d['lang'],'holdings':d['holdings'],'cover':d['cover'] })
		
		if len(d['lccSubject']) == 1:
			s1 = d['lccSubject'][0]
			s2 = None
			s3 = None
			s4 = None
			s5 = None
			s6 = None
			s7 = None
			s8 = None
			s9 = None
		if len(d['lccSubject']) == 2:
			s1 = d['lccSubject'][0]
			s2 = d['lccSubject'][1]
			s3 = None
			s4 = None
			s5 = None
			s6 = None
			s7 = None
			s8 = None
			s9 = None
		if len(d['lccSubject']) == 3:
			s1 = d['lccSubject'][0]
			s2 = d['lccSubject'][1]
			s3 = d['lccSubject'][2]
			s4 = None
			s5 = None
			s6 = None
			s7 = None
			s8 = None
			s9 = None
		if len(d['lccSubject']) == 4:
			s1 = d['lccSubject'][0]
			s2 = d['lccSubject'][1]
			s3 = d['lccSubject'][2]
			s4 = d['lccSubject'][3]
			s5 = None
			s6 = None
			s7 = None
			s8 = None
			s9 = None
		if len(d['lccSubject']) == 5:
			s1 = d['lccSubject'][0]
			s2 = d['lccSubject'][1]
			s3 = d['lccSubject'][2]
			s4 = d['lccSubject'][3]
			s5 = d['lccSubject'][4]
			s6 = None
			s7 = None
			s8 = None
			s9 = None

		if len(d['lccSubject']) == 6:
			s1 = d['lccSubject'][0]
			s2 = d['lccSubject'][1]
			s3 = d['lccSubject'][2]
			s4 = d['lccSubject'][3]
			s5 = d['lccSubject'][4]
			s6 = d['lccSubject'][5]
			s7 = None
			s8 = None
			s9 = None

		if len(d['lccSubject']) == 7:
			s1 = d['lccSubject'][0]
			s2 = d['lccSubject'][1]
			s3 = d['lccSubject'][2]
			s4 = d['lccSubject'][3]
			s5 = d['lccSubject'][4]
			s6 = d['lccSubject'][5]
			s7 = d['lccSubject'][6]
			s8 = None
			s9 = None

		if len(d['lccSubject']) == 8:
			s1 = d['lccSubject'][0]
			s2 = d['lccSubject'][1]
			s3 = d['lccSubject'][2]
			s4 = d['lccSubject'][3]
			s5 = d['lccSubject'][4]
			s6 = d['lccSubject'][5]
			s7 = d['lccSubject'][6]
			s8 = d['lccSubject'][7]
			s9 = None

		if len(d['lccSubject']) == 9:
			s1 = d['lccSubject'][0]
			s2 = d['lccSubject'][1]
			s3 = d['lccSubject'][2]
			s4 = d['lccSubject'][3]
			s5 = d['lccSubject'][4]
			s6 = d['lccSubject'][5]
			s7 = d['lccSubject'][6]
			s8 = d['lccSubject'][7]
			s9 = d['lccSubject'][8]



		found1 = None
		for c1 in hiearchyx['children']:
			if c1['name'] == s1['name']:
				found1 = c1

		if not found1:
			hiearchyx['children'].append({"name": s1['name'], "code":s1['code'],"children": [],  'hash':hash_lookup[0]})

			for c1 in hiearchyx['children']:
				if c1['name'] == s1['name']:
					found1 = c1



		if s2 == None:
			if 'value' not in found1:
				found1['value'] = 1
			else:
				found1['value'] = found1['value'] + 1			
			continue

		found2 = None
		for c2 in found1['children']:
			if c2['name'] == s2['name']:
				found2 = c2

		if not found2:
			found1['children'].append({"name": s2['name'], "code":s2['code'],"children": [],  'hash':hash_lookup[1]})
			for c2 in found1['children']:
				if c2['name'] == s2['name']:
					found2 = c2


		if s3 == None:
			if 'value' not in found2:
				found2['value'] = 1
			else:
				found2['value'] = found2['value'] + 1
			continue


		found3 = None
		for c3 in found2['children']:
			if c3['name'] == s3['name']:
				found3 = c3

		if not found3:
			found2['children'].append({"name": s3['name'], "code":s3['code'],"children": [],  'hash':hash_lookup[2]})
			for c3 in found2['children']:
				if c3['name'] == s3['name']:
					found3 = c3


		if s4 == None:
			if 'value' not in found3:
				found3['value'] = 1
			else:
				found3['value'] = found3['value'] + 1
			continue			



		found4 = None
		for c4 in found3['children']:
			if c4['name'] == s4['name']:
				found4 = c4

		if not found4:
			found3['children'].append({"name": s4['name'], "code":s4['code'],"children": [],  'hash':hash_lookup[3]})
			for c4 in found3['children']:
				if c4['name'] == s4['name']:
					found4 = c4


		if s5 == None:
			if 'value' not in found4:
				found4['value'] = 1
			else:
				found4['value'] = found4['value'] + 1
			continue



		found5 = None
		for c5 in found4['children']:
			if c5['name'] == s5['name']:
				found5 = c5

		if not found5:
			found4['children'].append({"name": s5['name'], "code":s5['code'],"children": [],  'hash':hash_lookup[4]})
			for c5 in found4['children']:
				if c5['name'] == s5['name']:
					found5 = c5


		if s6 == None:
			if 'value' not in found5:
				found5['value'] = 1
			else:
				found5['value'] = found5['value'] + 1
			continue

		found6 = None
		for c6 in found5['children']:
			if c6['name'] == s6['name']:
				found6 = c6

		if not found6:
			found5['children'].append({"name": s6['name'], "code":s6['code'],"children": [],  'hash':hash_lookup[5]})
			for c6 in found5['children']:
				if c6['name'] == s6['name']:
					found6 = c6


		if s7 == None:
			if 'value' not in found6:
				found6['value'] = 1
			else:
				found6['value'] = found6['value'] + 1
			continue

		found7 = None
		for c7 in found6['children']:
			if c7['name'] == s7['name']:
				found7 = c7

		if not found7:
			found6['children'].append({"name": s7['name'], "code":s7['code'],"children": [],  'hash':hash_lookup[6]})
			for c7 in found6['children']:
				if c7['name'] == s7['name']:
					found7 = c7


		if s8 == None:
			if 'value' not in found7:
				found7['value'] = 1
			else:
				found7['value'] = found7['value'] + 1
			continue



		found8 = None
		for c8 in found7['children']:
			if c8['name'] == s8['name']:
				found8 = c8

		if not found8:
			found7['children'].append({"name": s8['name'], "code":s8['code'],"children": [],  'hash':hash_lookup[7]})
			for c8 in found7['children']:
				if c8['name'] == s8['name']:
					found8 = c8


		if s9 == None:
			if 'value' not in found8:
				found8['value'] = 1
			else:
				found8['value'] = found8['value'] + 1
			continue


		found9 = None
		for c9 in found8['children']:
			if c9['name'] == s9['name']:
				found9 = c9

		if not found9:
			found8['children'].append({"name": s9['name'], "code":s9['code'],"children": [],  'hash':hash_lookup[8]})
			for c9 in found8['children']:
				if c9['name'] == s9['name']:
					found9 = c9


		if 'value' not in found9:
			found9['value'] = 1
		else:
			found9['value'] = found9['value'] + 1
		continue




#Fall of the Republic and establishment

		# if d['lccSubject'][0] not in hiearchyx:
		# 	hiearchyx[d['lccSubject'][0]] =  {"name": d['lccSubject'][0],"children": []}

		# if len(d['lccSubject']) == 1:
		# 	continue

		# if d['lccSubject'][1] not in hiearchyx[d['lccSubject'][0]['children']:
		# 	hiearchyx[d['lccSubject'][0]]['children'] =  {"name": d['lccSubject'][1],"children": []}

		# if len(d['lccSubject']) == 2:
		# 	continue

print(largest)
print(json.dumps(hiearchyx,indent=2))
json.dump(hiearchyx, open('../data/lcc_hiearchy_1929_pd.json','w'))
# json.dump(hash_data, open('hash_data.json','w'))

hash_metadata = {}
for h in hash_data:

	vol_chunks = list(chunks(hash_data[h]['volumes'],1000))

	print(hash_data[h]['subject'],len(vol_chunks))


	hash_metadata[h] = hash_data[h]
	del hash_metadata[h]['volumes']

	hash_metadata[h]['pages'] = len(vol_chunks)

	counter = 0
	for page in vol_chunks:
		counter+=1
		json.dump(page, open(f'../data/hashdata/{h}_{counter}.json','w'))

json.dump(hash_metadata, open('../data/hash_metadata.json','w'),indent=2)





