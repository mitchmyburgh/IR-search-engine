from PyDictionary import PyDictionary
dictionary=PyDictionary()

def getSynonyms(word):
    return dictionary.synonym(word.replace(" ", "").replace("\n", ""))
