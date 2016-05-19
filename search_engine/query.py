# Modified from code provided by Hussein Suleman
# Search engine querying code
# 16 May 2016

import re
import math
import sys
import os

import porter

import parameters

stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'a',
'b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v',
'w','x','y','z',]

def call_query(query, collection, i, brf, brf_count, brf_number_words, brf_from, stopwords):
    # clean query
    if parameters.case_folding:
       query = query.lower ()
    query = re.sub (r'[^ a-zA-Z0-9]', ' ', query)
    query = re.sub (r'\s+', ' ', query)
    query_words = query.split (' ')

    # create accumulators and other data structures
    accum = {}
    filenames = []
    p = porter.PorterStemmer ()

    # get N
    f = open ("indexes/"+collection+"_index_N", "r")
    N = eval (f.read ())
    f.close ()

    # get document lengths/titles
    titles = {}
    f = open ("indexes/"+collection+"_index_len", "r")
    lengths = f.readlines ()
    f.close ()

    # get index for each term and calculate similarities using accumulators
    for term in query_words:
        if stopwords and (term in stop_words):
            continue
        if term != '':
            if parameters.stemming:
                term = p.stem (term, 0, len(term)-1)
            if not os.path.isfile ("indexes/"+collection+"_index/"+term):
                continue
            f = open ("indexes/"+collection+"_index/"+term, "r")
            lines = f.readlines ()
            idf = 1
            if parameters.use_idf:
               df = len(lines)
               idf = 1/df
               if parameters.log_idf:
                  idf = math.log (1 + N/df)
            for line in lines:
                mo = re.match (r'([0-9]+)\:([0-9\.]+)', line)
                if mo:
                    file_id = mo.group(1)
                    tf = float (mo.group(2))
                    if not file_id in accum:
                        accum[file_id] = 0
                    if parameters.log_tf:
                        tf = (1 + math.log (tf))
                    accum[file_id] += (tf * idf)
            f.close()

    # parse lengths data and divide by |N| and get titles
    for l in lengths:
       mo = re.match (r'([0-9]+)\:([0-9\.]+)\:(.+)', l)
       if mo:
          document_id = mo.group (1)
          length = eval (mo.group (2))
          title = mo.group (3)
          if document_id in accum:
             if parameters.normalization:
                accum[document_id] = accum[document_id] / length
             titles[document_id] = title

    # print top ten results
    results = sorted (accum, key=accum.__getitem__, reverse=True)
    print(results)
    final_result = []
    #print(collection+" "+query)
    for c in range (min (len (results), 10)):
       #print ("{0:10.8f} {1:5} {2}".format (accum[result[c]], result[c], titles[result[c]]))
       final_result.append([accum[results[c]], results[c]])
    if (brf and brf_count == 0):
        total = 0
        for result in results:
            if total >= brf_from:
                break
            total += 1
            document = result
            print(document)
            print(str(i))
            #accumulation = result[0]
            f = open("indexes/tf-idf/testbed"+str(i)+"_document_"+str(document)+"_tf-idf", "r")
            lines = f.readlines()
            f.close()
            c = 0
            d = 0
            word = ""
            while (c < brf_number_words and len(lines) > d):
                mo = lines[d].split(":")
                if (word == mo[1].replace("\n", "") or mo[1].replace("\n", "") in stop_words):
                    d+=1
                    continue
                word = mo[1].replace("\n", "")
                query+=" "+word
                d+=1
                c+=1
        final_result = call_query(query, collection, i, brf, brf_count+1, brf_number_words, brf_from, stopwords)
    return final_result
