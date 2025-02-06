import glob
import requests
import gzip
import json
import os
import shutil

count=0

for file in glob.glob("../data/hathi_web/*"):
	
	count=count+1

	# if count < 40000:
	# 	continue

	# print(file)
	try:
		web_f=gzip.open(file,'rb')
		web_f_content=web_f.read()
	except:
		print("BAd", file)
		os.remove(file)

	web_data = json.loads(web_f_content)
	web_f.close()
	# print(json.dumps(web_data,indent=2))


	# print(hid,defseq)
	if 'HT.params.defaultSeq '  in web_data:
		hid = web_data['HT.params.id ']			
		defseq = web_data['HT.params.defaultSeq ']

		url = f"https://babel.hathitrust.org/cgi/imgsrv/image?id={hid}&seq={defseq}&height=800"

		hid=hid.replace("/",'_')
		hid=hid.replace(":",'_')		

		# if hid == 'uc1.$b114973':
		# 	print(url)
		# continue

		if os.path.isfile(f"../data/covers/{hid}.jpg") == True:
			continue

		with requests.get(url, stream=True) as r:
			with open(f"../data/covers/{hid}.jpg", 'wb') as f:
				shutil.copyfileobj(r.raw, f)


		
		print(count,url)