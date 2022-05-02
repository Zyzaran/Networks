#include <stdlib.h>
#include <iostream>
#include <stdio.h>
#include <string.h>
#include <string>
#include <cstdlib>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netdb.h>
#include <unistd.h>
#include <errno.h>
#include <arpa/inet.h>
#include <sys/wait.h>
#include <signal.h>
#include <time.h>
#include <sys/ioctl.h>
#include <linux/netdevice.h>

using namespace std;

bool debug=false;
int MAXBUFLEN= 140;
int portc=3943;

int makeport(){
	time_t timeseed;
	time(&timeseed);
	srand(timeseed);
	return 1024 + rand()%16382+1;
}


string toBinaryRec(int variable){
	if(variable==0){ return "0";
	}
	if(variable==1){return "1";
	}
	if(variable%2!=0){
		return toBinaryRec(variable/2)+"1";
	}else {
		return toBinaryRec(variable/2)+"0";
	}

}

string toBinary(int num, int slots){
	string ournum=toBinaryRec(num);
	string padding;
	for(int i=0;i<slots-ournum.size();i++){
		padding+="0";
	}
	ournum = padding+ournum;
	return ournum;
}


int servermode(){
	cout<<"Welcome to chat!"<<endl;
    int sockStatus = socket(AF_INET, SOCK_STREAM, 0);
    char buf[2048];
    socklen_t addresslength;

    struct sockaddr_in serverIn;

    if(sockStatus<0){
    	perror("There was an error opening a socket serverside. Closing");
    	return -1;
    }

    bzero((char *) &serverIn, sizeof(serverIn));
    serverIn.sin_family=AF_INET;
    serverIn.sin_addr.s_addr = INADDR_ANY;
    serverIn.sin_port=htons(portc);
    int bindstatus=bind(sockStatus, (struct sockaddr *) &serverIn, sizeof(serverIn));

    if(sizeof(serverIn)<0){
    	perror("There was a binding error serverside. Closing");
    	return -1;
    }

    // Calling that sweet sweet ifconfig
   	struct ifconf ifconfig;
	struct ifreq ifr[50];
	ifconfig.ifc_buf = (char *) ifr;
	ifconfig.ifc_len = sizeof ifr;
    
    if (ioctl(sockStatus, SIOCGIFCONF, &ifconfig) == -1) {
    	perror("there was an error in grabbing our own IP. Exiting.");
    	return -1;
  	}

    char ips[INET_ADDRSTRLEN];
    struct sockaddr_in *s_in = (struct sockaddr_in *) &ifr[1].ifr_addr;

    if (!inet_ntop(AF_INET, &s_in->sin_addr, ips, sizeof(ips))) {
      perror("inet_ntop error was had while looking Ip. Exiting");
      return -1;
    }

    printf("Waiting for a connection on %s port %i\n", ips, portc);
    bool sending=false;
    sockaddr_in clientIn;

    listen(sockStatus,3);
    addresslength = sizeof (clientIn);
    int clientSock=accept(sockStatus, (struct sockaddr *) &clientIn, &addresslength);
    cout<<"Found a friend! You recieve first."<<endl;
    while(true){
    	
    	
    	if(clientSock<0){
    		perror("There was an issue serverside accepting client. Exiting");
    		return -1;
    	}
    	

    	memset(&buf,0,sizeof(buf));
    	recv(clientSock, (char*)&buf,sizeof(buf),0);
    	string packetData(buf);
    	int recversion=stoi(packetData.substr(0,16),0,2);
    	int reccontentlength=stoi(packetData.substr(16,31),0,2);
    	recversion=ntohs(recversion);
    	reccontentlength=ntohs(reccontentlength);
    	//cout<<"this is recversion "<<recversion<<endl;
    	//cout<<"this is reccontent "<<reccontentlength<<endl;
    	string clientwords=packetData.substr(32,32+reccontentlength);

    	cout<<"Friend: "<<clientwords<<endl;

    	//Send a message back to the client
    	bool nomessage=true;
        string servermessage;
        char buff[141];
    	while(nomessage){
    		cout<<"You: ";
    		getline(cin, servermessage);
    		memset(&buff, 0, sizeof(buff));
        	strcpy(buff, servermessage.c_str());
    		if(servermessage.size()>140){
    			printf("Error: Input too long.\n");
    		} else{
    			nomessage=false;
    		}
    	}
    	nomessage=true;

    	// Serialize here
       	string version = toBinary(htons(457), 16);
       	string contentlength=toBinary(htons(servermessage.size()), 16);
       	int offset=0;
       	for(int t=0;t<version.size();t++){
       		buf[offset+t]=version[t];
       	}
       	offset+=version.size();

        for(int t=0;t<contentlength.size();t++){
       		buf[offset+t]=contentlength[t];
        }
        offset+=contentlength.size();

        for(int t=0;t<sizeof(buff);t++){
       		buf[offset+t]=buff[t];
        }

    	send(clientSock, (char *)&buf, sizeof(buf), 0);
    }


    close(sockStatus);
}



int clientmode(char *ip, char *port){
	char buf[2048];
	sockaddr_in serverIn;
	int socks=socket(AF_INET, SOCK_STREAM,0);

	bzero((char *)&serverIn,sizeof(serverIn));

	struct hostent* serverinfo= gethostbyname(ip);

	serverIn.sin_family=AF_INET;
	serverIn.sin_addr.s_addr=inet_addr(inet_ntoa(*(struct in_addr*)*serverinfo->h_addr_list));
	serverIn.sin_port=htons(atoi(port));

	cout<<"Connecting to server...";	
	int socketStatus=connect(socks,(sockaddr *) &serverIn,sizeof(serverIn));

	if(socketStatus<0){
		perror("There was an error clientside while socketing. Exiting");
		return -1;
	}

	cout<<" Connected!"<<endl;

	cout<<"Connected to a friend! You send first."<<endl;
   	char buff[141];
	while(true){
    	bool nomessage=true;
    	string clientmessage;
    	while(nomessage){
    		cout<<"You: ";

    		getline(cin, clientmessage);
    		memset(&buff, 0, sizeof(buff));
        	strcpy(buff, clientmessage.c_str());


    		if(clientmessage.size()>140){
    			printf("Error: your message is too long! try again.\n");
    		} else{
    			nomessage=false;
    		}
    	}

       	string version = toBinary(htons(457), 16);
       	string contentlength=toBinary(htons(clientmessage.size()), 16);
       	int offset=0;
       	for(int t=0;t<version.size();t++){
       		buf[offset+t]=version[t];
       	}
       	offset+=version.size();

        for(int t=0;t<contentlength.size();t++){
       		buf[offset+t]=contentlength[t];
        }
        offset+=contentlength.size();

        for(int t=0;t<sizeof(buff);t++){
       		buf[offset+t]=buff[t];
        }



    	nomessage=true;

    	send(socks,(char*)&buf,sizeof(buf),0);
    	char servermessage[240];
    	recv(socks,(char *)&buf,sizeof(buf),0);
    	string packetData(buf);
    	int recversion=stoi(packetData.substr(0,16),0,2);
    	int reccontentlength=stoi(packetData.substr(16,31),0,2);
    	recversion=ntohs(recversion);
    	reccontentlength=ntohs(reccontentlength);
    	//    	cout<<"this is recversion "<<recversion<<endl;
    	//cout<<"this is reccontent "<<reccontentlength<<endl;
    	string serverwords=packetData.substr(32,32+reccontentlength);

    	cout<<"Friend: "<<serverwords<<endl;

	}
	close(socks);
}











bool isProperIP(char* &ip){
	string IP(ip);
	return IP.find_first_not_of("0123456789.")==string::npos;
}
bool isProperPort(char* &port){
	string Port(port);
	return Port.find_first_not_of("0123456789")==string::npos;
}

int main(int argc, char * argv[]){
	if(debug){
		cout<<"\t\t----====>WARNING: DEBUG ENABLED<====----"<<endl;
	}
	char *port;
	char * ipaddress;
	if(argc>5){
		cout<<"Too many arguments provided. Invoke ./chat.exe -h for help.\n-Exiting-"<<endl;
		return -1;
	}

	if(argc==2){
	//Help mode
		if(strcmp(argv[1],"-h")==0){
			if(debug){cout<<"\tEntering Help Mode"<<endl;}
			printf("How to invoke the following methods:\n\t  Help Mode: ./chat.exe -h\n\tServer Mode: ./chat.exe\n\tClient Mode: ./chat.exe -s <Server IP> -h <Port>\n\t\t  OR ./chat.exe -h <Port> -s <Server IP>\n-Exiting-\n");
			return 0;
		}else{
			cout<<"\tInvalid Flag\n-Exiting-"<<endl;
			return -1;
		}
	}
	//Client mode
	if(argc==5){
		int pfound=false;
		int sfound=false;
		//cout<<"\tEntering Client Mode"<<endl;
		if(strcmp(argv[1],"-s")==0){
			ipaddress = argv[2];
		} else if (strcmp(argv[1],"-p")==0){
			port = argv[2];
		} else {
			cout<<"Invalid flag.\n-Exiting-"<<argv[1]<<endl;
			return -1;
		}
		
		if(strcmp(argv[3], "-s")==0 && sfound ==false){
			ipaddress = argv[4];
		} else if (strcmp(argv[3],"-p")==0 && pfound ==false){
			port = argv[4];
		} else {
			cout<<"Invalid flag.\n-Exiting-"<<endl;
			return -1;
		}

		if(!isProperIP(ipaddress)){
			printf("%s is not a proper IP-Address. An IP-Address has only Numbers, and '.'s.\n -EXITING-\n", ipaddress);
			return -1;
		}
		if(!isProperPort(port)){
			printf("%s is not a proper Port. A Port has only Numbers.\n -EXITING-\n", port);
			return -1;
		}

		clientmode(ipaddress,port);

	}else{
	//Server mode
		if(argc==1){
			//cout<<"\tEntering Server Mode"<<endl;
			servermode();
		}
	}


	return 0;


}