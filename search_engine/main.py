import os
import sys
from datetime import datetime
from math import log

from index import index
from query import call_query

## Index the files
def create_index():
	startTime = datetime.now()
	#index the testbeds
	for i in range(1, 17):
		index("testbeds/testbed"+str(i), i)

	print ("Time taken: "+str(datetime.now() - startTime))

## Run the queries
def run_queries(output_dir, output_file):
	#create the output folder
	try:
		os.makedirs(output_dir)
	except:
		pass
	#clean the output file
	f = open (output_dir+"/"+output_file, 'w')
	f.write("Testbed,Query,MAP,NDCG,MAPwithBRF,NDCGwithBRF,MAPwithSW,NDCGwithSW,MAPwithThes,NDCGwithThes,MAPwithThesAndStop,NDCGwithThesAndStop,MAPwithCom,NDCGwithCom\n")
	f.close()

	for i in range(1, 17): #loop over testbeds
		for j in range(1, 6): #loop over queries
			#read the query
			f = open ("testbeds/testbed"+str(i)+"/query."+str(j))
			#process the query on the appropriate testset
			read_query = f.read().replace("\n", "")
			f.close()
			result = call_query(read_query, "testbed"+str(i), i, False, 0, 0, 0, False, False)
			result_brf = call_query(read_query, "testbed"+str(i), i, True, 0, 1, 1, False, False) #12, 18
			result_stop_words = call_query(read_query, "testbed"+str(i), i, False, 0, 0, 0, True, False)
			result_thesauri = call_query(read_query, "testbed"+str(i), i, False, 0, 0, 0, False, True)
			result_stop_and_thesauri = call_query(read_query, "testbed"+str(i), i, False, 0, 0, 0, True, True)
			result_combined = call_query(read_query, "testbed"+str(i), i, True, 0, 1, 1, True, True)
			# calculate the scores
			base_scores = calculate_scores(result, i, j)
			brf_scores = calculate_scores(result_brf, i, j)
			stop_words_scores = calculate_scores(result_stop_words, i, j)
			thesauri_scores = calculate_scores(result_thesauri, i, j)
			stop_and_thesauri_scores = calculate_scores(result_stop_and_thesauri, i, j)
			combined_scores = calculate_scores(result_combined, i, j)
			#write MAP and NDCG to file
			if (base_scores and brf_scores):
				f = open (output_dir+"/"+output_file, 'a')
				f.write(str(i)+","+str(j)+","+str(base_scores[0])+","+str(base_scores[1])+","+
				str(brf_scores[0])+","+str(brf_scores[1])+","+
				str(stop_words_scores[0])+","+str(stop_words_scores[1])+","+
				str(thesauri_scores[0])+","+str(thesauri_scores[1])+","+
				str(stop_and_thesauri_scores[0])+","+str(stop_and_thesauri_scores[1])+","+
				str(combined_scores[0])+","+str(combined_scores[1])+"\n")
				f.close()


## Loop over possible params for BRF
def check_params():
	best_scores = {}
	for i in range(1, 17): #loop over testbeds
		for j in range(1, 6): #loop over queries
			for k in range (31):#31
				if not (k in best_scores):
					best_scores[k] = {}
				for l in range (21):#21
					if not (l in best_scores[k]):
						best_scores[k][l] = []
					result_brf = call_query(read_query, "testbed"+str(i), i, True, 0, k, l, False, False)
					brf_scores = calculate_scores(result_brf, i, j, output_dir, output_file)
					if (brf_scores):
						best_scores[k][l].append(brf_scores)
	calculate_best_average(best_scores)

## Calculate the best average MAP and NDCG scores and print them out
def calculate_best_average(best_scores):
	best_average_map = 0
	best_average_map_for_NDCG = 0
	k_map = 0
	l_map = 0
	best_average_NDCG = 0
	best_average_NDCG_for_map = 0
	k_NDCG = 0
	l_NDCG = 0
	for k in range (31):#number of words
		for l in range (21):#number of documents
			total_map = 0
			total_NDCG = 0
			#calculate avaerage
			for i in best_scores[k][l]:
				total_map += i[0]
				total_NDCG += i[1]
			#check for best avaerage map
			if (total_map/len(best_scores[k][l]) > best_average_map):
				best_average_map = total_map/len(best_scores[k][l])
				best_average_map_for_NDCG = total_NDCG/len(best_scores[k][l])
				k_map = k
				l_map = l
			#check for best average NDCG
			if (total_NDCG/len(best_scores[k][l]) > best_average_NDCG):
				best_average_NDCG = total_NDCG/len(best_scores[k][l])
				best_average_NDCG_for_map = total_map/len(best_scores[k][l])
				k_NDCG = k
				l_NDCG = l
	#Print output
	print("MAP = "+str(best_average_map)+" NDCG = "+str(best_average_map_for_NDCG)+" for k = "+str(k_map)+" for l = "+str(l_map))
	print("NDCG = "+str(best_average_NDCG)+" MAP = "+str(best_average_NDCG_for_map)+" for k = "+str(k_NDCG)+" for l = "+str(l_NDCG))

# calculate scores in result for testbed i, query j
def calculate_scores(result, i, j):
	#read the relevance judgements
	f = open ("testbeds/testbed"+str(i)+"/relevance."+str(j))
	relevance = f.readlines()
	f.close()
	MAPs = []
	NDCGs = []
	#handle problems in the relevance files
	#handle files with random newlines at the end
	while (len(relevance) != 0 and relevance[len(relevance)-1] =="\n"):
		del relevance[len(relevance)-1]
	#handle files with less than 200 relevance judgements - not really much we can do here
	if (len(relevance) != 200):
		print("That's disapointing. Testbed "+str(i)+" failed for query "+str(j))
		return False
	else:
		#calculate MAP
		precision = [] # set of average precision values at n
		relevant = 0 # number of relevant articles
		for c in range (len(result)):
			if (int(relevance[int(result[c][1])-1].strip()) != 0): # if article is relevant
				relevant += int(relevance[int(result[c][1])-1].strip())
				precision.append(relevant/((c+1)*2))
			else: # article not relevant
				precision.append(relevant/((c+1)*2))
			print(relevant)
		#cacluate mean of the average precisions
		total = 0
		for c in range(len(precision)):
			total+= precision[c]
		meanap = total/(len(precision)*2)

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
		return [meanap, NDCG]

if __name__ == '__main__':
	if len(sys.argv)==1:
		print ("Syntax: main.py <command = index | query>")
		exit(0)
	if (sys.argv[1] == "index"):
		create_index()
	elif (sys.argv[1] == "query"):
		run_queries("output","output.csv")
	elif (sys.argv[1] == "query_param"):
		check_params()
