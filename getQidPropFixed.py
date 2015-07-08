import urlparse,urllib,urllib2
import time
import os
import json
import csv
import pickle
def queryToJson():
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]

        #infile = opener.open('https://wdq.wmflabs.org/api?q=BETWEEN[569,1200,2015]%20AND%20BETWEEN[570,1200,2015]')
        #infile = opener.open('https://wdq.wmflabs.org/api?q=BETWEEN[569,0,2015]')
        infile = opener.open('https://wdq.wmflabs.org/api?q=BETWEEN[569,0,2015]&props=569,570&format=json')
        return infile

def fixurl(url):
    # turn string into unicode
    if not isinstance(url,unicode):
        url = url.decode('utf8')

    # parse it
    parsed = urlparse.urlsplit(url)

    # divide the netloc further
    userpass,at,hostport = parsed.netloc.rpartition('@')
    user,colon1,pass_ = userpass.partition(':')
    host,colon2,port = hostport.partition(':')

    # encode each component
    scheme = parsed.scheme.encode('utf8')
    user = urllib.quote(user.encode('utf8'))
    colon1 = colon1.encode('utf8')
    pass_ = urllib.quote(pass_.encode('utf8'))
    at = at.encode('utf8')
    host = host.encode('idna')
    colon2 = colon2.encode('utf8')
    port = port.encode('utf8')
    path = '/'.join(  # could be encoded slashes!
        urllib.quote(urllib.unquote(pce).encode('utf8'),'')
        for pce in parsed.path.split('/')
    )
    query = urllib.quote(urllib.unquote(parsed.query).encode('utf8'),'=&?/')
    fragment = urllib.quote(urllib.unquote(parsed.fragment).encode('utf8'))

    # put it back together
    netloc = ''.join((user,colon1,pass_,at,host,colon2,port))
    return urlparse.urlunsplit((scheme,netloc,path,query,fragment))    

def parseJson(jsonObject):
        englishLangDict = {}
        qidLangDict = {}
        englishName=""
        resultDict = json.load(jsonObject)
        wikidataPeopleList = resultDict['items']
        wikiProps = resultDict['props']
        dobList = wikiProps['569']
        dobDict = {}
        #print "dob len is", len(dobList)
        #print "dob - ", dobList[0][0]
        for dobitem in dobList:
            if dobitem[1] == "time":
                #print "qid is", dobitem[0]
                standardTime = dobitem[2]
                #print standardTime
                year = int(standardTime[8:12])
                j = 12
                while standardTime[j] == '-':
                    j = j + 1
                month = ''
                while standardTime[j] != '-':
                    month = month + standardTime[j]
                    j = j + 1
                month = int(month)
                while standardTime[j] == '-':
                    j = j + 1
                date = ''
                while standardTime[j] != 'T':
                    date = date + standardTime[j]
                    j = j + 1
                date = int(date)
                formattedDate = str(year)+ "/" + str(month) + "/" + str(date)
                dobDict[dobitem[0]] = formattedDate
                #break
        #print dobDict

        deathList = wikiProps['570']
        #print "death list len is",len(deathList), deathList[100][2]
        deathDict = {}
        for deathitem in deathList:
            if deathitem[1] == "time":
                #print "qid is", deathitem[0]
                standardTime = deathitem[2]
                #print standardTime
                year = int(standardTime[8:12])
                j = 12
                while standardTime[j] == '-':
                    j = j + 1
                month = ''
                while standardTime[j] != '-':
                    month = month + standardTime[j]
                    j = j + 1
                month = int(month)
                while standardTime[j] == '-':
                    j = j + 1
                date = ''
                while standardTime[j] != 'T':
                    date = date + standardTime[j]
                    j = j + 1
                date = int(date)
                formattedDate = str(year)+ "/" + str(month) + "/" + str(date)
                deathDict[deathitem[0]] = formattedDate

        print "Total number of person pages in wikipedia are", len(wikidataPeopleList)

        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]

        entityDict = {}
        langDict = {}   

        #Limit is 50 IDs per request

        #strList = []
        person = ""
        for i in range(0,len(wikidataPeopleList),50):
        #for i in range(0,1):
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
                            #infile = opener.open('http://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q19921990&format=json')
                    except:
                            print "Got a ECONNRESET. Trying again...\n"

            wikipediaJSON = json.load(infile)
	    
	    #print wikipediaJSON['entities'].keys()             
            for entity in wikipediaJSON['entities'].keys():
	            localLangDict={}
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
                                            valueToAdd = labelDict[label]['value']
                                            localLangDict[keyToAdd] = valueToAdd
                                            if(keyToAdd=='enwiki'):
                                                englishLangDict[valueToAdd] = wikidataPeopleList[i]
                                                dob = -1
                                                deathDate = -1
                                                try:
                                                    dob = dobDict[entity[1:]]
                                                except:
                                                    pass
                                                try:
                                                    deathDate = deathDict[entity[1:]]
                                                except:
                                                    pass
                                                qidLangDict[entity]=(localLangDict,dob,deathDate)
                    else:
                            sitelinks = wikipediaJSON['entities'][entity]['sitelinks']
                            dob = -1
                            deathDate = -1
                            try:
                                dob = dobDict[entity[1:]]
                            except:
                                pass
                            try:
                                deathDate = deathDict[entity[1:]]
                            except:
                                pass
                            personLangList=[]
                            for link in sitelinks.keys():				    
                                    langTitle = sitelinks[link]['title']
                                    langCode = link[0:link.index("wiki")]
                                    unicodeTitle = langTitle.encode('utf-8')
                                    query = 'http://'+langCode+'.wikipedia.org/w/api.php?action=query&titles='+langTitle+'&prop=info&format=json'
                                    query = query.replace(" ", "%20")
                                    query=fixurl(query)
                                    pageLength = 0
                                    try:
                                        infile = opener.open(query)
                                        lengthJSON = json.load(infile)
                                        pageDict = lengthJSON["query"]["pages"]
                                        pageLength = 0
                                        for pageKey in pageDict.keys():
                                            propDict = pageDict[pageKey]
                                            if "length" in propDict.keys():
                                                pageLength = propDict["length"]
                                            break
                                    except:
                                        pass
                                    localLangDict[str(link)] = (langTitle,pageLength)
                            qidLangDict[entity]=(localLangDict,dob,deathDate)
	    if (i+50)%10000 == 0:
                        fileName = "qid_prop_dict2_" + str((i+50)/10000) + ".json"
                        fileNameToDelete = "qid_prop_dict2_" + str((i+50)/10000 - 1)+".json"
                        os.system("rm "+fileNameToDelete)
                        json.dump(qidLangDict,open(fileName,'w'))
                        print "Extracted", i + 50, "persons"	    
        with open('qidLangDictLabels.pickle', 'wb') as handle:
          pickle.dump(qidLangDict, handle)            

        with open('enLangDictLabels.pickle', 'wb') as handle:
          pickle.dump(englishLangDict, handle)            
	with open('qidLangDictLabels.json', 'w') as fp:
          json.dump(qidLangDict,fp)
wikidataJSON = queryToJson()
parseJson(wikidataJSON)
