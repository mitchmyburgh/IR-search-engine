import os
import re
import sys

import porter
import parameters

def index(folder_name, i):
	# Make index directories
	try:
		os.makedirs("indexes/testbed"+str(i)+"_index")
	except:
		pass
	data = {}
	#read in files
	for j in range(1, 201):
		document = ''
		f = open (folder_name+"/document."+str(j), "r", encoding = "ISO-8859-1")
		if parameters.case_folding:
			for line in f.readlines():
				document += line.lower()+" "
		else:
			for line in f.readlines():
				document += line+" "
		if (document != ''):
			data["document."+str(j)] = document 
		f.close()

	# document length/title file
	g = open ("indexes/"+ "testbed"+str(i) + "_index_len", "w")

	# create inverted files in memory and save titles/N to file
	index = {}
	N = len (data.keys())
	p = porter.PorterStemmer ()
	for key in data:
	    content = re.sub (r'[^ a-zA-Z0-9]', ' ', data[key])
	    content = re.sub (r'\s+', ' ', content)
	    words = content.split (' ')
	    doc_length = 0
	    for word in words:
	        if word != '':
	            if parameters.stemming:
	                word = p.stem (word, 0, len(word)-1)
	            doc_length += 1
	            if not word in index:
	                index[word] = {key:1}
	            else:
	                if not key in index[word]:
	                    index[word][key] = 1
	                else:
	                    index[word][key] += 1
	    print (key, doc_length, "document."+str(j), sep=':', file=g) 

	# document length/title file
	g.close ()

	for key in index:
	    f = open ("indexes/testbed"+str(i)+"_index/"+key, "w")
	    for entry in index[key]:
	        print(key+" , "+entry)
	        print (entry, index[key][entry], sep=':', file=f)
	    f.close ()
	# write N
	f = open ("indexes/testbed"+str(i)+"_index_N", "w")
	print (N, file=f)
	f.close ()
