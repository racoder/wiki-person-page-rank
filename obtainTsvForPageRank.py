import json
import os
from lxml import etree

dicts_from_file = json.load(open("../../rakeshc/final_language_dict_182.txt"))

def createPersonTsv(language,wikifilename):
	#doc = etree.parse(wikifilename)
	count =0
	languagePerson = "tsvs/" + language+"Persons.tsv"
	if language+"wiki" not in dicts_from_file.keys():
		print "language", language, "not present in dictionary"
		with open("nokeys.txt", "a") as myfile:
			myfile.write(language+"\n")
		return 0
	PersonList  = set(dicts_from_file[language+"wiki"])#returnLangPerson(language)
	print "number of persons in language", language, "are", len(PersonList)
	
	with open(languagePerson, "a") as myfile:
		i = 0
		j = 0
		for ev,pchild in etree.iterparse(wikifilename, events=('end',), tag='p'):
			#print "pchild is",pchild.text
			#linkChildrenCompleted = False
			if i%1000 == 0:
				print "Scanned",i,language,"pages"
			i = i + 1
			entryRow = []
			pageNotAPerson = False
			for child in pchild.iterchildren():
				if child.tag == 't':
					#if i%1000 == 0:
					#print "Scanned",i,"pages"
					if child.text not in PersonList:
						pageNotAPerson = True
						child.clear()
						break
					else:
						#print "found a person page"
						entryRow.append(child.text)

			if pageNotAPerson:
				continue

			foundPersonLink = False
			for child in pchild.iterchildren():
				if child.tag == 'l':
					j = j + 1
					if j%1000 == 0:
						print "Scanned", j, language, "links"
					if child.text not in PersonList:
						#print "link not a person..skipping"
						continue
					#print "found a person link"
					foundPersonLink = True
					entryRow.append(child.text)
					child.clear()
					if child.getprevious() is not None:	
						del child.getparent()[0]
			
			if foundPersonLink:
				pchild.clear()
				while pchild.getprevious() is not None:
					del pchild.getparent()[0]
				entryRow.append("\n")
				strEntry = '\t'.join(entryRow).encode('utf-8')
				myfile.write(strEntry)

if __name__ == "__main__":
        fp = open("languages-with-dumps.txt","r")
        li = fp.readlines()
        for lang in li:
                language = lang.strip()
                wikifilename = language+"wiki-links.xml"
                #print language
                if (os.path.isfile(wikifilename)):
                        #print "Found: ",language
                        createPersonTsv(language,wikifilename)
