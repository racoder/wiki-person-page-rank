#! /bin/bash           

while read line           
do           
    myWiki='./generate/$line'
    mysuffix='Persons.tsv' 
    myWiki2='Rank'
    myprefix='./Ranks/'
    myWiki=$myWiki$mysuffix
    myWiki2=$line$myWiki2
    mvn exec:java -Dexec.mainClass=edu.umd.cloud9.example.pagerank.SequentialPageRank    -Dexec.args="-input $myWiki -jump 0.15" > $myprefix$myWiki2

done <all-language-codes.txt      


