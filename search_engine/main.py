import os
import sys
from datetime import datetime
from math import log

from index import index
from query import query

def create_index():
	#create the indexes folder
	try:
		os.mkdir ("indexes")
	except:
		print("fail")
		pass

	startTime = datetime.now()
	#index teh testbeds
	for i in range(1, 17):
		index("testbeds/testbed"+str(i), i)

	print ("Time taken: "+str(datetime.now() - startTime))

def run_queries(output_dir, output_file):
	#create teh output folder
	try:
		os.makedirs(output_dir)
	except:
		pass
	#clean the output file
	f = open (output_dir+"/"+output_file, 'w')
	f.write("Testbed,Query,MAP,NDCG\n")
	f.close()
	for i in range(1, 17): #loop over testbeds
		for j in range(1, 6): #loop over queries
			#read the query 
			f = open ("testbeds/testbed"+str(i)+"/query."+str(j))
			#process the query on the appropriate testset
			result = query(f.read().replace("\n", ""), "testbed"+str(i), i)
			f.close()

			#read the relevance judgements
			f = open ("testbeds/testbed"+str(i)+"/relevance."+str(j))
			relevance = f.readlines()
			f.close()

			#handle problems in the relevance files
			#handle files with random newlines at the end
			while (len(relevance) != 0 and relevance[len(relevance)-1] =="\n"):
				del relevance[len(relevance)-1]
			#handle files with less than 200 relevance judgements - not really much we can do here
			if (len(relevance) != 200):
				print("That's disapointing. Testbed "+str(i)+" failed for query "+str(j))
			else:
				#calculate MAP
				precision = [] # set of average precision values at n
				relevant = 0 # number of relevant articles
				for c in range (len(result)):
					if (int(relevance[int(result[c][1])-1].strip()) != 0): # if article is relevant
						relevant += 1
						precision.append(relevant/(c+1))
					else: # article not relevant
						precision.append(relevant/(c+1))
				#cacluate mean of the average precisions 
				total = 0
				for c in range(len(precision)):
					total+= precision[c]
				meanap = total/len(precision)

				# Calculate NDCG
				#calculate DCG
				DCG = 0
				for c in range (len(result)):
					DCG += int(relevance[int(result[c][1])-1].strip())/log(c+2, 2)
				count2 = 0
				count1 = 0
				# find the number of 2's and if necessary the number of ones
				for c in relevance:
					if (int(c) == 2):
						count2 += 1
						if (count2 >= len(result)): # stop cos we have enough 2's
							break
					elif (int(c)==1):
						count1 += 1
				# calculate the IDCG based on the number of 2's and 1's that could potentially appear in the first 10 results
				IDCG = 0
				for c in range (len(result)):
					if (count2 > 0):
						count2-=1
						IDCG += 2/log(c+2,2)
					elif (count1 > 0):
						count1-= 1
						IDCG += 2/log(c+2,2)

				NDCG = DCG/IDCG # calculating NDCG

				#write MAP and NDCG to file
				f = open (output_dir+"/"+output_file, 'a')
				f.write(str(i)+","+str(j)+","+str(meanap)+","+str(NDCG)+"\n")
				f.close()



if __name__ == '__main__':
	if len(sys.argv)==1:
		print ("Syntax: main.py <command = index | query>")
		exit(0)
	if (sys.argv[1] == "index"):
		create_index()
	elif (sys.argv[1] == "query"):
		run_queries("output","output.csv")