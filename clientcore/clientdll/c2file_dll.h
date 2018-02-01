#ifndef c2file_H__
#define c2file_H__

DWORD read_frame(HANDLE my_handle, char * buffer, DWORD max)
void write_frame(HANDLE my_handle, char * buffer, DWORD length)
HANDLE start_beacon(char * payload, DWORD length)

#endif