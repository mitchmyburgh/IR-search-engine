# Modified from code provided by Hussein Suleman
# Search engine indexing code
# 16 May 2016

import os
import re
import sys
import math

import porter
import parameters

def index(folder_name, i):
	# Make index directories
	try:
		os.makedirs("indexes/testbed"+str(i)+"_index")
	except:
		pass
	try:
		os.makedirs("indexes/tf-idf/")
	except:
		pass
	data = {}
	print("indexing testbed"+str(i), end="")
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
			data[str(j)] = document
		f.close()

	# document length/title file
	g = open ("indexes/"+ "testbed"+str(i) + "_index_len", "w")

	# create inverted files in memory and save titles/N to file
	index = {}
	N = len (data.keys())
	p = porter.PorterStemmer ()
	for key in data:
		#write over dtf
		tf_idf = open ("indexes/tf-idf/"+ "testbed"+str(i) + "_document_"+str(key)+"_tf-idf", "w")
		tf_idf.write("")
		tf_idf.close()

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
		print (key, doc_length, key, sep=':', file=g) 

	# document length/title file
	g.close ()

	tf_idf_arr = []

	for key in index:
		f = open ("indexes/testbed"+str(i)+"_index/"+key, "w")
		for entry in index[key]:
			# additionally calculate the tf-idf for use in Blind relevance feedback
			#tf_idf = open ("indexes/tf-idf/"+ "testbed"+str(i) + "_document_"+str(entry)+"_tf-idf", "a")
			print(key+" , "+entry)
			print (entry, index[key][entry], sep=':', file=f)
			tf = float(index[key][entry])
			idf = 1
			if parameters.use_idf:
				df = len(index[key])
				idf = 1/df
				if parameters.log_idf:
					idf = math.log (1 + N/df)
			tf_idf_arr.append([tf*idf, key])
			#print (tf*idf, key, sep=':', file=tf_idf) # format tf-idf: word
			#tf_idf.close()
		f.close ()
	# write N
	f = open ("indexes/testbed"+str(i)+"_index_N", "w")
	print (N, file=f)
	f.close ()
	# sort on tf_idf
	for j in range(1, 201):
		#tf_idf = open ("indexes/tf-idf/"+ "testbed"+str(i) + "_document_"+str(j)+"_tf-idf", "r")
		#lines = tf_idf.readlines()
		#tf_idf.close()
		tf_idf_arr.sort(key=lambda k: (k[0], k[1]), reverse=True)
		tf_idf = open ("indexes/tf-idf/"+ "testbed"+str(i) + "_document_"+str(j)+"_tf-idf", "w")
		for line in tf_idf_arr:
			print("working")
			print (line[0], line[1], sep=':', file=tf_idf)
		tf_idf.close()


