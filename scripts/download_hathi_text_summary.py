import gzip
import json
import requests
import glob
import os.path
from openai import OpenAI
from typing import List, Literal
from pydantic import BaseModel
import tiktoken



def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

class Smmary(BaseModel):
    summary: str
    generes: List[str]

# class Smmary(BaseModel):
#     has_racist_words: bool
#     list_of_words_sentiments: List[str]


lang_lookup ={}
with gzip.open('../data/hathi_collection_final_dataset.ndjson.gz','rt') as f:
    for line in f:
        data = json.loads(line)
        lang_lookup[str(data['ht_bib_key'])] = data['language']




client = OpenAI(
    base_url="https://api.studio.nebius.ai/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY"),
)    


for file in glob.glob("../data/hathi_text/*.json"):

    if '3793437'  in file:
        continue
    if '3614775'  in file:
        continue
    if '9659945'  in file:
        continue
    if '3245538'  in file:
        continue
    if '1188998'  in file:
        continue
    if '1229754'  in file:
        continue

    if '6028981'  in file:
        continue
    if '3574465'  in file:
        continue


    hid = file.split('/')[-1].split(".")[0]


    if lang_lookup[hid] in ['arm','yid']:
        continue



    # if os.path.isfile(file.replace('hathi_text','hathi_summaries')) == True:
    if os.path.isfile(file.replace('hathi_text','hathi_summaries_real')) == True:


        print(file, 'skipp')
        continue

    print("lang:",lang_lookup[hid])

    print(file)

    d = json.load(open(file))
    if len(d) > 50:
        d = d[0:50]
    text = "\n".join(d)

    tokens = num_tokens_from_string(text, "o200k_base")

    if tokens > 131072:
        d = json.load(open(file))
        if len(d) > 40:
            d = d[0:40]
        text = "\n".join(d)




    print("--------------------------------")
    print(file)
    print(tokens)



    completion = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct",
        messages=[
            {
                "role": "system",
                # "content": """
                #     You are evaluating old text for racist words or sentiment. Does the follow text have racist words or sentiments in them based on today's standard? Your response is in JSON. If it does then set 'has_racist_words' key to true, and list words and examples in 'list_of_words_sentiments' key.
                # """
                "content" : """
                    You are a helpful assistant that only answers in English. You are processing the first 50 pages of a book and generating JSON about it. Generate a book blurb for the back cover, a short paragraph in English that describes the book without revealing too much of the plot, keep it general, a teaser for the text. Only use the text provided, do not make up any information, if the summary is not in English translate it to English, use the JSON key summary. Also generate a list of literary Genres that best describe the text in English, if the terms are not English then translate them to English, use the JSON key generes. Your response must be in English. If the source text is not English translate it when writing your response in English.  Here is the text to process: 
                """
            },
            {
                "role": "user",
                "content": text
            }
        ],

        temperature=0,
        max_tokens=10000,
        # response_format={
        #     "type": "json_object"
        # },
        extra_body={
            "guided_json": Smmary.model_json_schema()
        }        
    )


    # print(completion)
    result = completion.to_dict()
    # result = completion.to_json()
    # result = json.loads(result)
    # print(result)
    try:
        result = json.loads(result['choices'][0]['message']['content'], strict=False)
    except:
        continue
    
    # json.dump(result, open(file.replace('hathi_text','hathi_summaries'),'w'),indent=2)
    json.dump(result, open(file.replace('hathi_text','hathi_summaries_real'),'w'),indent=2)



    print(result)
