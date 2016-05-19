import os
import sys
from datetime import datetime
from math import log

from index import index
from query import call_query

def create_index():
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
	f.write("Testbed,Query,MAP,NDCG,MAPwithBRF,NDCGwithBRF,MAPwithSW,NDCGwithSW,MAPwithThes,NDCGwithThes,MAPwithThesAndStop,NDCGwithThesAndStop,MAPwithCom,NDCGwithCom\n")
	f.close()
	num_words = {}
	num_sources = {}
	best_combo = {}
	for i in range(1, 17): #loop over testbeds
		for j in range(1, 6): #loop over queries
			#read the query
			f = open ("testbeds/testbed"+str(i)+"/query."+str(j))
			#process the query on the appropriate testset
			read_query = f.read().replace("\n", "")
			f.close()
			result = call_query(read_query, "testbed"+str(i), i, False, 0, 0, 0, False, False)
			result_brf = call_query(read_query, "testbed"+str(i), i, True, 0, 10, 1, False, False) #12, 18
			result_stop_words = call_query(read_query, "testbed"+str(i), i, False, 0, 0, 0, True, False)
			result_thesauri = call_query(read_query, "testbed"+str(i), i, False, 0, 0, 0, False, True)
			result_stop_and_thesauri = call_query(read_query, "testbed"+str(i), i, False, 0, 0, 0, True, True)
			result_combined = call_query(read_query, "testbed"+str(i), i, True, 0, 10, 1, True, True)
			# calculate the scores
			base_scores = calculate_scores(result, i, j, output_dir, output_file)
			brf_scores = calculate_scores(result_brf, i, j, output_dir, output_file)
			stop_words_scores = calculate_scores(result_stop_words, i, j, output_dir, output_file)
			thesauri_scores = calculate_scores(result_stop_words, i, j, output_dir, output_file)
			stop_and_thesauri_scores = calculate_scores(result_stop_and_thesauri, i, j, output_dir, output_file)
			combined_scores = calculate_scores(result_combined, i, j, output_dir, output_file)

			# for k in range (21):
			# 	for l in range (21):
			# 		result_brf = call_query(read_query, "testbed"+str(i), i, True, 0, k, l, False)
			# 		brf_scores = calculate_scores(result_brf, i, j, output_dir, output_file)
			# 		if (brf_scores and base_scores and base_scores[0]< brf_scores[0] and base_scores[1]< brf_scores[1]):
			# 			print("We got a better result with brf_number_words="+str(k)+" brf_from="+str(l)+" for testbed="+str(i)+" for query="+str(j))
			# 			if str(k) in num_words:
			# 				num_words[str(k)] += 1
			# 			else:
			# 				num_words[str(k)] = 1
			# 			if str(l) in num_sources:
			# 				num_sources[str(l)] += 1
			# 			else:
			# 				num_sources[str(l)] = 1
			# 			if (str(k)+str(l)) in best_combo:
			# 				best_combo[(str(k)+str(l))] += 1
			# 			else:
			# 				best_combo[(str(k)+str(l))] = 1
			# check for best brf combination


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
	# print(num_words)
	# print(num_sources)
	# print(best_combo)
	# maxi = 0
	# out = ""
	# for key in best_combo:
	# 	if best_combo[key] > maxi:
	# 		out = key
	# print(out)

def calculate_scores(result, i, j, output_dir, output_file):
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
