from PyDictionary import PyDictionary
dictionary=PyDictionary()
import os
import re

def getSynonyms(word):
	return dictionary.synonym(word.replace(" ", "").replace("\n", ""))

def buildModule(wordlist, outputfile):
	thesaurus = {}
	for word in wordlist:
		thesaurus[word.replace(" ", "").replace("\n", "")] = getSynonyms(word)
	print(thesaurus)
	f = open(outputfile+".py", "w")
	f.write("#Generated Code for getting Synonyms\n")
	f.write("#19 May 2016\n")
	f.write("thesaurus = "+str(thesaurus)+"\n")
	f.write("def getSynonyms(word):\n")
	f.write("\treturn thesaurus[word.replace(' ', '').replace('\\n', '')]\n")
	f.close()




if __name__ == "__main__":
	words=[]
	for root, dirs, files in os.walk("testbeds"):
		for name in files:
			if name[0:len(name)-2]=="query":
				file = open(os.path.join(root, name), 'r')
				for line in file:
					a=line.strip()
					tempArr=a.split(" ")
					for w in tempArr:
						if (w.lower() not in words):
							word = re.sub('[!@#$.?]', '', w.lower())
							words.append(word)
				#print(name)
				#print

	print(words)
	buildModule(words, "output")
