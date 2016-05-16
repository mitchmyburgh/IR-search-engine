import os
import sys
from datetime import datetime

from index import index
from query import query

def create_index():
	try:
		os.mkdir ("indexes")
	except:
		pass

	startTime = datetime.now()
	for i in range(1, 17):
		index("testbeds/testbed"+str(i), i)

	print ("Time taken: "+str(datetime.now() - startTime))

def run_queries():
	try:
		os.mkdir ("output")
	except:
		pass
	for i in range(1, 17):
		for j in range(1, 6):
			f = open ("testbeds/testbed"+str(i)+"/query."+str(j))
			result = query(f.read().replace("\n", ""), "testbed"+str(i), i)
			f.close()
			f = open ("testbeds/testbed"+str(i)+"/relevance."+str(j))
			relevance = f.readlines()
			f.close()
			while (len(relevance) != 0 and relevance[len(relevance)-1] =="\n"):
				del relevance[len(relevance)-1]
			if (len(relevance) != 200):
				print("That's disapointing. Testbed "+str(i)+" failed for query "+str(j))
			#for i in range (min (len (result), 10)):



if __name__ == '__main__':
	if len(sys.argv)==1:
		print ("Syntax: main.py <command = index | query>")
		exit(0)
	if (sys.argv[1] == "index"):
		create_index()
	elif (sys.argv[1] == "query"):
		run_queries()