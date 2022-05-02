import sys

debug=False
bool isProperIP(ip):
	IP = ip
	return IP.find_first_not_of("0123456789.")==string::npos

bool isProperPort(port):
	Port= port
	return Port.find_first_not_of("0123456789")==string::npos

void steppingStone():
	#haha
	return -1

void reader():
	#:(
	return -1
	
int main(int argc, char * sys.argv[]):
	if(debug):
		print "\t\t----====>WARNING: DEBUG ENABLED<====----"
	
	string port
	string ipaddress
	if(argc>5):
		print "Too many arguments provided. Invoke ./chat.exe -h for help.\n-Exiting-"
		return -1
	

	if(argc==2):
	#Help mode
		if strcmp(sys.argv[1],"-h") ==0:
			if(debug):
				print "\tEntering Help Mode"
			print "How to invoke the following methods:\n\t  Help Mode: ./chat.exe -h\n\tServer Mode: ./chat.exe\n\tClient Mode: ./chat.exe -s <Server IP> -h <Port>\n\t\t  OR ./chat.exe -h <Port> -s <Server IP>\n-Exiting-\n"
			return 0
		else:
			print "\tInvalid Flag\n-Exiting-"
			return -1
		
	
	#Client mode
	if(argc==5):
		int pfound=false
		int sfound=false
		if debug: 
			print "\tEntering Client Mode"
		if(strcmp(sys.argv[1],"-s")==0):
			ipaddress = sys.argv[2]
		 else if (strcmp(sys.argv[1],"-p")==0):
			port = sys.argv[2]
		 else :
			print "Invalid flag.\n-Exiting-", sys.argv[1]
			return -1
		
		
		if(strcmp(sys.argv[3], "-s")==0 && sfound ==false):
			ipaddress = sys.argv[4]
		else if (strcmp(sys.argv[3],"-p")==0 && pfound ==false):
			port = sys.argv[4]
		else :
			print "Invalid flag.\n-Exiting-"
			return -1
		

		if(!isProperIP(ipaddress)):
			print ipaddress, " is not a proper IP-Address. An IP-Address has only Numbers, and '.'s.\n -EXITING-\n"
			return -1
		
		if(!isProperPort(port)):
			print port, " is not a proper Port. A Port has only Numbers.\n -EXITING-\n"
			return -1
		

		clientmode(ipaddress,port)

	else:
	#Server mode
		if(argc==1):
			if debug:
				print "\tEntering Server Mode"
			servermode()
		
	


	return 0


