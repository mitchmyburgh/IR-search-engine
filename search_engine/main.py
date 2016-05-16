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
	for i in range(1, 17):
		index("query", "testbeds/testbed"+str(i), i)

if __name__ == '__main__':
	if len(sys.argv)==1:
		print ("Syntax: main.py <command = index | query>")
		exit(0)
	if (sys.argv[1] == "index"):
		create_index()
	elif (sys.argv[1] == "query"):
		print("query")