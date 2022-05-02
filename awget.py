import socket
import random
import re

import urllib
import sys
import urlparse

lPort = random.randint(1, 1024 * 5) + 1024 #random default port
debug = False
defaultChainName='chaingang.txt'

def readChainFileStrict(fileName = defaultChainName):
	ssPairs=[]
	chainfile = open(fileName, 'r')
	entryCount=0

	#get number
	currentLine = chainfile.readline()
	if currentLine == "":
		print "Chain File Error: File is empty.\n\t -Exiting-"
		exit()

	currentLine=currentLine.strip("\r\n")
	tokens = currentLine.split(" ")

	if len(tokens)>1:
		print "Chain File Error: Too many characters before receiving list count.\n\t -Exiting-"
		exit()

	if tokens[0].isdigit():
		entryCount=tokens[0]
	else:
		print "Chain File Error: First character set is not a number.\n\t-Exiting-"


	while True:

		currentLine=chainfile.readline()
		if currentLine=="":
			if debug: print "EOF reached"
			break

		currentLine=currentLine.strip("\r\n")
		tokens = currentLine.split(" ")

		if len(tokens)>2:
			print "Chain File Error: extra characters found in ip port pairs.\n\t -Exiting-"

		if not isProperIP(tokens[0]) or not isProperPort(tokens[1]):
			print "Chain File Error: IP or Port in file is not valid: "+str(tokens)+".\n\t -Exiting-"
			exit()
		entryPair=[tokens[0],int(tokens[1])]
		ssPairs.append(entryPair)
	return entryCount, ssPairs





def readChainFile(fileName = defaultChainName):
	ssPairs=[]
	chainfile = open(fileName, 'r')

	seekingListLen = True
	clearPrePad=False
	consumingPairs=False

	entryCount=0
	entryPair=[]

	currentLine= chainfile.readline()


	if currentLine == "":
		print "Chain File Error: File is empty.\n\t -Exiting-"
		exit()


	while True:
		if currentLine=="":
			if debug: print "EOF reached"
			break

		currentLine=currentLine.strip("\r\n")

		tokens = currentLine.split(" ")

		if (seekingListLen):
			if len(tokens)>1:
				print "Chain File Error: Too many characters before receiving list count.\n\t -Exiting-"
				exit()

			elif (tokens[0].isdigit()):
				if debug: print "found entry count"
				entryCount=int(tokens[0])
				seekingListLen=False
				clearPrePad=True
				currentLine=chainfile.readline()
				currentLine=currentLine.strip("\r\n")
				tokens=currentLine.split(" ")

			elif (tokens[0] != ""):
				print "Chain File Error: First non-space character found was not a number. ["+str(tokens)+"]\n\t -Exiting-"
				exit()
		
		if(clearPrePad):
			if debug: print "Clearing padding before sets"
			if len(tokens)==1 and tokens[0]=="":
				pass
				#Perfectly acceptable line here.
			elif len(tokens)==2:
				clearPrePad=False
				consumingPairs=True
			else:
				print "Chain File Error: Unnacceptable characters before start of list.["+str(tokens)+"]\n\t -Exiting-"
				exit()

		if(consumingPairs):
			if debug: print "Grabbing pairs"
			if len(tokens)==1 and tokens[0]=="":
				pass
				#Perfectly acceptable line here.
			elif len(tokens)==2:
				if not isProperIP(tokens[0]) or not isProperPort(tokens[1]):
					print "Chain File Error: IP or Port in file is not valid: "+str(tokens)+".\n\t -Exiting-"
					exit()
				entryPair=[tokens[0],int(tokens[1])]
				ssPairs.append(entryPair)
			else:
				print "Chain File Error: Unnacceptable characters before start of list.\n\t -Exiting-"
				exit()



		currentLine= chainfile.readline()
	if debug: print entryCount, ssPairs

	if entryCount!= len(ssPairs):
		print "Chain File Error: The number of pairs and specified pair count do not match["+str(entryCount-len(ssPairs))+"]\n\t -Exiting-"
		exit()

	return entryCount, ssPairs



def readChainFileOld(fileName = defaultChainName):

	ssPairs=[]
	chainfile = open(fileName, 'r')
	seekingListLen = True
	eofFound=False
	entryCount=0


	entryPair=[]
	entriesFound=0
	currentToken="" 


	while not(eofFound):

		element = str(chainfile.read(1))
		if(debug):
			print "This is our current element: "+element

		if not element:
			print "EOF reached."
			entryPair.append(currentToken)
			ssPairs.append(entryPair)
			break

		if(seekingListLen):
			#check for unnacceptable starting characters here

			if element.isalpha():
				print "The file was not formatted correctly. Reason: isalpha tripped where there should be no alpahnumeric at start of file\n\t -Exiting-"
				exit()

			if element.isdigit():
				if debug: print "Length found"
				seekingListLen=False
				entryCount=int(element)

				#consume all characters until first numeric value is found
				element = str(chainfile.read(1)) # consume one element to assert that there's a space, or newline between host num and entries
				assert not element.isdigit(), "Assertion Error: There must be a space or newline/return between list number and first entry\n\t-Exiting-"

				element = str(chainfile.read(1))


				if debug: print "Cleaning space before list"

				while not element.isdigit():
					element = chainfile.read(1)
					if not(element == " " or element == "\n" or element == "\t" or element == "\r") and not element.isdigit():
						print "Error: Unexpected character before first entry:["+element+"].\n\t -Exiting-"
						exit()

				currentToken=str(currentToken+element)
		else:
			if (element == " " or element == "\n" or element == "\r" or element =="\t"):
				if debug: print "Token finished: " + str(currentToken)

				print entriesFound%2

				if bool(re.search(r"\d",currentToken)):
					entryPair.append(currentToken)

				currentToken=""
				if entriesFound%2==0 and entriesFound!=0:
					if debug: print "IP, Port pair found: "+str(entryPair)
					ssPairs.append(entryPair)
					entryPair=[]
					while not element.isdigit():
						element = chainfile.read(1)
						if not(element == " " or element == "\n" or element == "\t" or element == "\r") and not element.isdigit():
							print "Error: Unexpected character before next entry:["+element+"].\n\t -Exiting-"
							exit()
					currentToken=str(currentToken+element)

				entriesFound+=1
			else:
				currentToken=str(currentToken+element)

	# check that all ips are valid and there as many as the file said there were
	for i in ssPairs:
		if not isProperIP(i[0]) or not isProperPort(i[1]):
			print "Error: IP or Port in file is not valid: "+str(i)+".\n\t -Exiting-"
			exit()
	if entryCount != len(ssPairs):
		print "Error: Number of entries in file does not match entryNum given.\n\t-Exiting-"
		exit()

	return entryCount, ssPairs



def unencodeChain(rawstring):

	ssPairs=[]
	rawlist = rawstring.split(" ")
	filename= rawlist[0]
	entryCount=rawlist[1]
	foundentries=0
	entryPair=[]
	for i in range(len(rawlist)-2):
		entryPair.append(rawlist[2+i])
		foundentries+=1
		if foundentries%2==0:
			ssPairs.append(entryPair)
			entryPair=[]
	return filename, entryCount, ssPairs

def encodeChain(fileName, entryNum, ssPairs):
	finalstring= str(fileName) +" "+str(entryNum)

	pairstring =""
	for i in range(len(ssPairs)):
		pairstring = pairstring+ " " + str(ssPairs[i][0]) +" "+str(ssPairs[i][1])

	return finalstring + pairstring

def isProperIP(ip):
	print ip
	try:
		socket.inet_aton(str(ip))
	except socket.error:
		return False
	return True

def isProperPort(port):
	return re.search(r'[^0123456789]', port) == None

#Main Thread
#BIND to a random ip from list, send the initial string
#listen on port for file return
#Recieve file and then save it
#exit
if len(sys.argv) > 3:
	print "Input ERROR: Too many arguments provided. \n\t-Exiting-"
	sys.exit()

paircount, pairs = 0, []
fileUrl=""
if len(sys.argv) == 3:
	fileUrl=sys.argv[1]
	paircount, pairs = readChainFile(sys.argv[2])
elif len(sys.argv) == 2:
	fileUrl=sys.argv[1]
	paircount, pairs  = readChainFile()
else:
	print "Input ERROR: Too few arguments provided. \n\t-Exiting-"
	sys.exit()

chosenIndex =random.randint(0,len(pairs)-1)
destinationIP, destinationPort = pairs[chosenIndex][0], pairs[chosenIndex][1]
#decrement remaining elements and pop off chosen pair
print "Request: "+fileUrl
print "chainlist is"
for u in range(len(pairs)):
	print str(pairs[u][0])+", "+str(pairs[u][1])
pairs.pop(chosenIndex)
paircount=int(paircount)-1
print "next SS is "+str(destinationIP)+" "+str(destinationPort)

sendString = encodeChain(fileUrl,paircount,pairs)

if debug: print destinationIP, destinationPort
sendsock = None
try:
	sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sendsock.connect((destinationIP,int(destinationPort)))
except:
	print "General error: Socket was unable to connect to IP Port Pair.\n\t-Exiting-"
sendsock.send(sendString)

chunkSize=2048
fileNameShort=fileUrl.replace("http://","")
fileName = fileNameShort[fileNameShort.rfind("/")+1:]

if (fileNameShort == fileName or fileName=="" or "." not in fileName):
	
	fileName = "index.html"



file= open(fileName,"w+")
print "waiting for file..."
sendsock.settimeout(3*len(pairs)+1)
while True:
	try:
		data = sendsock.recv(chunkSize)
		if not data or data =="":
				break
	#print str(data)
		file.write(data)
	except:
		break
file.close()
print "Received file "+fileName
print "Goodbye!"
