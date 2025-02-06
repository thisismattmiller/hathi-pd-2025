import gzip
import json
import os.path
import glob
import re
import requests
from lingua import Language, LanguageDetectorBuilder
from langcodes import Language as LanguageCodes


languages = [Language.ARABIC,Language.ARMENIAN,Language.BULGARIAN,Language.CATALAN,Language.CHINESE,Language.CZECH,Language.DANISH,Language.DUTCH,Language.ENGLISH,Language.FINNISH,Language.FRENCH,Language.GERMAN,Language.GREEK,Language.HEBREW,Language.CROATIAN,Language.HUNGARIAN,Language.ICELANDIC,Language.INDONESIAN,Language.ITALIAN,Language.JAPANESE,Language.KOREAN,Language.LATIN,Language.BOKMAL,Language.POLISH,Language.PORTUGUESE,Language.ROMANIAN,Language.RUSSIAN,Language.SPANISH,Language.SERBIAN,Language.SWEDISH,Language.THAI,Language.TURKISH,Language.UKRAINIAN]
detector = LanguageDetectorBuilder.from_languages(*languages).build()


def isLcc(lcc):

    if re.match(r"[A-Z]+[0-9]+", lcc) != None:
        return True

    if len(lcc.split(" ")[0]) == 2:
        if re.match(r"[A-Z]+",lcc.split(" ")[0]) != None:
            return True
    
    return False

works = {}
editions = {}

count = 0

with_lcc_count={
    'oclc':0,
    'hathi_marc':0,
    'lccn_found':0,
    'name_title_lookup':0,
    'lcsh_check':0
}


gutenberg_data = json.load(open('../data/gutenberg_matches.json'))
gutenberg_lookup = {}
for g in gutenberg_data:
    gutenberg_lookup[g['hid']] = g['pg_id']


lccns_to_check = {}
name_titles_to_check = {}
all_langs = {}
lcsh_to_check ={}
lcsh_checked = json.load(open("../data/lcsh_checked.json"))
lccns_checked = json.load(open("../data/lccns_checked.json"))
name_titles_checked = json.load(open("../data/name_titles_checked.json"))

with gzip.open(f'../data/hathi_collection_final_dataset.ndjson.gz', "wb", compresslevel=9) as f_final:


    with gzip.open('../data/hathi_collection_with_marc_oclc_holdings.ndjson.gz','rt') as f:
        for line in f:
            # count=count+1
            data = json.loads(line)
            
            hid = data['ht_bib_key']


            if str(hid) in gutenberg_lookup:
                data['gutenberg'] = gutenberg_lookup[str(hid)]
            else:
                data['gutenberg'] = False



            genre_format = False
            if 'oclc_data' in data:
                if data['oclc_data']['format'] != None:
                    genre_format = data['oclc_data']['format']

            # print(data['marc']['leader'][6])

            if data['marc']['leader'][6] == 'c':
                genre_format = 'MsScr'

            if data['marc']['leader'][7] == 's':
                genre_format = 'Jrnl'

            if genre_format == False:
                if 'annual report' in data['title'].lower():
                    genre_format = 'Jrnl'
            if genre_format == False:
                if 'annuaire' in data['title'].lower():
                    genre_format = 'Jrnl'
            if genre_format == False:
                if 'bulletin' in data['title'].lower():
                    genre_format = 'Jrnl'
            if genre_format == False:
                if 'report o' in data['title'].lower():
                    genre_format = 'Jrnl'
            if genre_format == False:
                if 'brief' in data['title'].lower():
                    genre_format = 'Jrnl'

            if genre_format == False:
                if 'magazine' in data['title'].lower():
                    genre_format = 'Jrnl'

            if genre_format == False:
                if 'year book' in data['title'].lower():
                    genre_format = 'Jrnl'

            if genre_format == False:
                if 'monthly' in data['title'].lower():
                    genre_format = 'Jrnl'

            if genre_format == False:
                if 'symphonie, no.' in data['title'].lower():
                    genre_format = 'MsScr'
            if genre_format == False:
                if 'report' == data['title'].lower().strip():
                    genre_format = 'Jrnl'
            if genre_format == False:
                if 'handbook' in data['title'].lower():
                    genre_format = 'Jrnl'


            if data['marc']['leader'][7] == 'm':
                genre_format = 'Book'

            if genre_format == False:
                # anything else just make a book
                genre_format = 'Book'


            data['genre_format'] = genre_format






            language = False
            if 'oclc_data' in data:
                if data['oclc_data']['language'] != None:
                    language = data['oclc_data']['language']

            if language == False:

                for field in data['marc']['fields']:
                    if '041' in field:
                        for subfield in field['041']['subfields']:
                            if 'a' in subfield:
                                if len(subfield['a']) == 3:
                                    # take the first good subfield a
                                    language = subfield['a']
                                    break


            if language == False or language == 'und' or language == 'zxx':
                language_result = detector.detect_language_of(data['title'])
                Language = language_result.iso_code_639_3.name

            data['language'] = language
            if language != None and language != False and language != '':
                data['language_name'] = LanguageCodes.get(language).display_name()
            else:
                data['language_name'] = False

            lcc_found = False
            # try to pull out the LCC 
            if 'oclc_data' in data:
                if data['oclc_data']['lcc'] != False and data['oclc_data']['lcc'] != None:
                    lcc_found = data['oclc_data']['lcc']
                    with_lcc_count['oclc']=with_lcc_count['oclc']+1

             
            if lcc_found == False:

                # maybe the MARC record has the LCC in it
                for field in data['marc']['fields']:
                    if '050' in field:
                        for subfield in field['050']['subfields']:
                            if 'a' in subfield:
                                subfield['a'] = subfield['a'].replace('[','').replace('f PL','PL')
                                if isLcc(subfield['a']) == True:
                                    lcc_found = subfield['a']
                                    with_lcc_count['hathi_marc']=with_lcc_count['hathi_marc']+1

                                else:
                                    print("Not LCC:", subfield['a'])

            if lcc_found == False:

                if hid in lccns_checked:
                    if 'lcc' in  lccns_checked[hid]:
                        lcc_found = lccns_checked[hid]['lcc']
                        with_lcc_count['lccn_found']=with_lcc_count['lccn_found']+1






            # grab the real title
            # maybe the MARC record has the LCC in it
            title = False
            for field in data['marc']['fields']:
                if '245' in field:
                    for subfield in field['245']['subfields']:
                        if 'a' in subfield:
                            title = subfield['a']

            data['marc_245_a'] = title





            if lcc_found == False:

                if data['lccn'] != "" and data['lccn'] != None:
                    
                    if title != False:

                        # print(data['author'], title)   
                        # print(data['lccn'])
                        lccn = data['lccn']

                        if len(re.findall(r"[0-9]{6,}",lccn)) > 0:

                            lccn = re.findall(r"[0-9]{6,}",lccn)[0]
                            lccns_to_check[hid] = {
                                'title':title,
                                'author': data['author'],
                                'lccn': lccn
                            }
                        else:
                            print("Bad lccn",data['lccn'])


            if lcc_found == False:
                if hid in name_titles_checked:
                    if 'lcc' in  name_titles_checked[hid]:
                        lcc_found = name_titles_checked[hid]['lcc']
                        with_lcc_count['name_title_lookup']=with_lcc_count['name_title_lookup']+1


            if lcc_found == False and 'oclc_data' in data:

                if data['oclc_data']['lcsh'] != None:
                    for lcsh in data['oclc_data']['lcsh']:
                        if lcsh in lcsh_checked:
                            if lcsh_checked[lcsh] != True:
                                lcc_found = lcsh_checked[lcsh]
                                with_lcc_count['lcsh_check']=with_lcc_count['lcsh_check']+1


            if lcc_found == False and 'oclc_data' in data:

                if data['oclc_data']['lcsh'] != None:
                    for lcsh in data['oclc_data']['lcsh']:
                        lcsh_to_check[lcsh] = True



            if lcc_found != False:
                count=count+1
                # print(count)


            data['lcc'] = lcc_found


            fiction_flag = False

            if data['lcc'] != False:
                if data['lcc'][0:2] == "PZ":
                    fiction_flag = True


            if data['lcc'] != False:
                if data['lcc'][0:2] == "PR":
                    num_search = re.search('PR([0-9]+)', data['lcc'], re.IGNORECASE)
                    if num_search:
                        try:
                            num = int(num_search.group(1))
                        except:
                            num = 0
                        if num > 78:
                            fiction_flag = True

            if data['lcc'] != False:
                if data['lcc'][0:2] == "PN":
                    num_search = re.search('PN([0-9]+)', data['lcc'], re.IGNORECASE)
                    if num_search:
                        try:
                            num = int(num_search.group(1))
                        except:
                            num = 0
                        if num > 5650:
                            fiction_flag = True

            if 'oclc_data' in data:
                fiction_flag = data['oclc_data']['fiction']





            data['fiction_flag'] = fiction_flag



            data['visual_flag'] = False
            data['seq_count'] = 0
            data['cover_id'] = ''

            try:

                web_data=gzip.open(f'../data/hathi_web/{hid}.json.gz','rb')
                web_data_content=web_data.read()
                web_data = json.loads(web_data_content)
                data['seq_count'] = web_data["HT.params.totalSeq "]
                data['cover_id'] = web_data["HT.params.id "]

                if 'HT.params.featureList ' in web_data:
                    total_pictures = 0
                    # print(web_data['HT.params.featureList '])
                    for seq in web_data['HT.params.featureList ']:
                        if 'features' in seq:
                            if 'IMAGE_ON_PAGE' in seq['features']:
                                total_pictures=total_pictures+1

                    data['total_pictures'] = total_pictures
                    if genre_format == 'Book':
                        if total_pictures/data['seq_count'] * 100 >= 75:
                            data['visual_flag'] = True

                            # if data['seq_count'] < 20:
                            if data['fiction_flag'] == True:
                                print(data['marc_245_a'], web_data['HT.params.RecordURL '])


            except:

                
                pass




            if os.path.isfile('../data/hathi_summaries/' + hid +'.json') == True:
                summary_data = json.load(open('../data/hathi_summaries/' + hid +'.json'))
                data['llama_3.3_preview'] = summary_data['summary']
                data['llama_3.3_generes'] = summary_data['generes']
            else:
                data['llama_3.3_preview'] = None
                data['llama_3.3_generes'] = None

            if os.path.isfile('../data/hathi_tests/' + hid +'.json') == True:
                tests = json.load(open('../data/hathi_tests/' + hid +'.json'))
                data['llama_3.3_content_test'] = tests['has_racist_words']
            else:
                data['llama_3.3_content_test'] = None








            # if data['fiction_flag'] == True:
            #     print(data['title'])
            #     print(data['author'])


            if data['lcc'] == False and 'oclc_data' in data:
                count=count+1
                # print(count, data['genre_format'], data['oclc_data'])
                # print(data)

            if 'oclc_data' in data:
                if data['oclc_data']['work'] in works:
                    works[data['oclc_data']['work']].append(data['oclc_data']['oclc'])
                else:
                    works[data['oclc_data']['work']] = [data['oclc_data']['oclc']]
                
            line_out = json.dumps(data) + '\n'
            f_final.write(line_out.encode("utf-8")) 



# for e in editions:
#     if editions[e] > 1:
#         print(e,editions[e])

for w in works:
    if len(works[w]) > 2:
        print(w,works[w])
#         if lcc_found == False:

#             name_titles_to_check[hid] = {
#                 'title':title,
#                 'author': data['author']
#             }

# json.dump(lccns_to_check,open('../data/lccns_to_check.json','w'),indent=2)
# json.dump(name_titles_to_check,open('../data/name_titles_to_check.json','w'),indent=2)
json.dump(lcsh_to_check,open('../data/lcsh_to_check.json','w'),indent=2)
print(with_lcc_count)