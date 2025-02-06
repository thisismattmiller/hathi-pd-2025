import gzip
import json
import os.path
import string 
import csv
from thefuzz import fuzz
import unicodedata
import multiprocessing
import tqdm



def normalize_string(s):
    s = str(s)
    s = s.translate(str.maketrans('', '', string.punctuation))
    s = " ".join(s.split())
    s = s.lower()
    s = s.casefold()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = s.replace('the','')
    return s

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]





pg_check = {}
# download from https://www.gutenberg.org/cache/epub/feeds/
with open('/Users/m/Downloads/pg_catalog.csv') as pgfile:

    reader = csv.DictReader(pgfile)
    for row in reader:
        pg_sr = {'author': row['Authors'].split(";")[0], 'title': row['Title'].split(";")[0]} 


        pg_check[row['Text#']] = pg_sr




def process_work(ht_to_check):


    # print(len(pg_check),ht_to_check)

    author = ht_to_check['author']
    title = ht_to_check['title']
    hid = ht_to_check['hid']

    for pg in pg_check:


        author_ratio = fuzz.ratio(normalize_string(pg_check[pg]['author']), normalize_string(author))
        title_ratio = fuzz.ratio(normalize_string(pg_check[pg]['title']), normalize_string(title))




        if author_ratio > 80 and title_ratio > 80:
            print('-------------')
            print(f'Title: {title_ratio} | {title} === {pg_check[pg]["title"]}')
            print(f'Author: {author_ratio} | {author} === {pg_check[pg]["author"]}')

            return ({
                'ht_author': author,
                'ht_title': title,
                'pg_title' : pg_check[pg]["title"],              
                'pg_author' : pg_check[pg]["author"],
                'pg_id': pg,
                'hid': hid

                })



    return False







if __name__ == '__main__':





    # count = 0
    to_check = []
    with gzip.open('../data/hathi_collection_final_dataset.ndjson.gz','rt') as f:

        for line in f:
            # count=count+1
            # if count % 100 == 0:
            #     print('\nHT File line: ',count)
            data = json.loads(line)        
            hid = data['ht_bib_key']


            title = data['marc_245_a'].strip()

            if title[-1] in string.punctuation:
                title = title[0:-1].strip()

            author = data['author'].strip()
            if len(author)>0:
                if author[-1] in string.punctuation:
                    author = author[0:-1].strip()


            to_check.append({
                'author': author,
                'title': title,
                'hid': hid
                })


            # if len(to_check) > 100:
            #     break




    # to_work = list(chunks(to_check,multiprocessing.cpu_count()))


    matches = []



    # start a multiprocessing with the naumber of workers as CPU cores we have
    the_pool = multiprocessing.Pool(multiprocessing.cpu_count())
    for result in tqdm.tqdm(the_pool.imap_unordered(process_work, to_check), total=len(to_check)):   
        # if result['error'] == False:
        #   works_lookup[result['work']['work_id']] = result['work']
        # else:
        #   errors.append(result['error_msg'])
        # print(result)
        if result != False:
            matches.append(result)

        


    # kill the workers
    the_pool.close()
    the_pool.join()

    json.dump(matches,open("../data/gutenber_matches.json",'w'),indent=2)
