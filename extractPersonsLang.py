import urllib2
import time
import os
import json
import csv


def queryToJson():
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]

	#infile = opener.open('https://wdq.wmflabs.org/api?q=BETWEEN[569,1200,2015]%20AND%20BETWEEN[570,1200,2015]')
	infile = opener.open('https://wdq.wmflabs.org/api?q=BETWEEN[569,0,2015]')
	return infile

def parseJson(jsonObject):
	resultDict = json.load(jsonObject)
	wikidataPeopleList = resultDict['items']

	print "Total number of person pages in wikipedia are", len(wikidataPeopleList)

	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]

	entityDict = {}
	langDict = {}

	#Limit is 50 IDs per request

	for i in xrange(0, len(wikidataPeopleList), 50):

		currentList = wikidataPeopleList[i:i+50]

		strList = []

		for person in currentList:
			strList.append('Q'+`person`+'|')
			#wikidataPeopleListStr = wikidataPeopleListStr+'Q'+str(person)+'|'

		wikidataPeopleListStr=''.join(strList)

		wikidataPeopleListStr = wikidataPeopleListStr[:-1]

		infile = None

		while infile is None:
			try:
				infile = opener.open('http://www.wikidata.org/w/api.php?action=wbgetentities&ids='+wikidataPeopleListStr+'&format=json')
			except:
				print "Got a ECONNRESET. Trying again...\n"

		wikipediaJSON = json.load(infile)

		for entity in wikipediaJSON['entities'].keys():

			if 'sitelinks' not in wikipediaJSON['entities'][entity]:
				print 'Entity', entity, 'doesn\'t have lang links'
				if 'labels' not in wikipediaJSON['entities'][entity].keys() or 'descriptions' not in wikipediaJSON['entities'][entity].keys():
					continue
				descriptionDict = wikipediaJSON['entities'][entity]['descriptions']
				labelDict = wikipediaJSON['entities'][entity]['labels']
				for label in labelDict.keys():
					print 'value is', labelDict[label]['value']
					if label in descriptionDict.keys():
						keyToAdd = label+u'wiki'
						if keyToAdd in langDict.keys():
							langDict[keyToAdd].append(labelDict[label]['value'])
						else:
							langDict[keyToAdd]=[labelDict[label]['value']]
			else:
				sitelinks = wikipediaJSON['entities'][entity]['sitelinks']

				#langDict = {}

				for link in sitelinks.keys():
					langTitle = sitelinks[link]['title']
					if link not in langDict.keys():
						langDict[link] = [langTitle]
					else:
						linkList = langDict[link]
						linkList.append(langTitle)


				#writer = csv.writer(open('persons_tmux_lang.csv', 'a'))

				#writer.writerow([langDict])
		if (i+50)%10000 == 0:
			fileName = "final_language_dict_" + str((i+50)/10000) + ".txt"
			fileNameToDelete = "final_language_dict_" + str((i+50)/10000 - 1)+".txt"
			os.system("rm "+fileNameToDelete)
			json.dump(langDict,open(fileName,'w'))
			print "Extracted", i + 50, "persons"

	#import pdb;pdb.set_trace()
	print "Done parsing - writing dictionary to a file..."
	#json.dump(langDict, open("final_language_dict.txt",'w'))


wikidataJSON = queryToJson()
parseJson(wikidataJSON)
