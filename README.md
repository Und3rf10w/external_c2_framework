# external_c2 framework
Python framework for usage with Cobalt Strike's External C2 specification as described in the [spec](https://www.cobaltstrike.com/downloads/externalc2spec.pdf).

The primary design goal is to be a very modular implementation of the external c2 spec that provides enough abstraction to easily implement C2 channels for Cobalt Strike. Ideally, all a user would have to do is create a `transport` module, an `encoder` module, and populate a configuration file to implement a new channel.

## Architecture
This project consists of three main parts:
 - Builder (not yet implemented)
 - Client
 - Server


### Builder
The builder dynamically builds client and server deployments based on the specified configuration. Ideally, the client would be able to be distributed as a single compiled file such as a dll or exe.

### Client
The client is essentially the payload that runs on the endpoint, referred to as `third-party client` within the spec. The logic of the client is primarily static:
1. Run any preparations need to be utilizing the `transport`
2. Receive the stager
3. Inject the stager and open the handle to the beacon
4. Obtain metadata from the beacon
5. Relay the metadata from the beacon to the C2 server via the `transport`
6. Watch the `transport` for new tasks
7. Relay new tasks to the beacon
8. Relay responses from the beacon via the `transport`
9. Repeat steps 6-8.

Configurations needed for the transport and encoding mechanisms are statically copied into the client. Function logic for transporting and encoding mechanisms are also statically copied into from their respective modules.

Process injection logic is determined from the builder.

### Server
The server is the application that brokers communication between the `client` and the `c2 server`, referred to as `third-party Client Controller` within the spec. The server logic is primarily static, but supports verbose and debug output to assist with development:
1. Parse the configuration
2. Import the specified encoding module
3. Import the specified transport module
4. Establish a connection to the c2 server
5. Request a stager from the c2 server
6. Encode the stager with the `encoder` module
7. Transport the stager with the `transport` module
8. Await for a metadata response from the client received via the `transport`
9. Decode the metadata with the `encoder` module
10. Relay the metadata to the c2 server.
11. Receive a new task from the c2 server.
12. Encode the new task
13. Relay the new task to the client via the `transport`
14. Receive for a response from the client received via the `transport`
15. Decode the response via the `encoder` module
16. Relay the response to the c2 server.
17. Repeat steps 11-16

The determination of which `encoder` and `transport` module the server imports is determined from the values stored in config.py.

No imports of ununsed `transport` or `encoder` modules are performed.

## Client and module shared functionality
The following tables describe shared functions between the `encoding` and `transport` modules, and the client. Shared functions are essentially the exact same code.

**A VERY IMPORTANT NOTE:** The data send to the client's `sendData` and `recvData` functions should be **raw data**, where data send to the transport module's `sendData` and `retrieveData` functions should **already be encoded or decoded as needed**.


### Transport module
| Transport Function | Client Function | Description |
| :---:| :---: | :--- |
| prepTransport | prepTransport | Performs any preconfigurations required to utilize the transport mechanism |
| sendData | sendData | Defines how data is sent through the transport mechanism |
| retrieveData | recvData | Defines how data is received through the transport mechanism

### Encoder Module
| Encoder Function | Client Function | Description |
| :---: | :---: | :--- |
| encode | encode | Defines modifications done to raw data to prepare it for transport
| decode | decode | Defines modifications done to raw data received from the transport to be relayed to its destination |

# How to use this
First, determine which transport and encoding module you'd like to use. We'll use `transport_gmail` and `encoder_b64url` for the following example.

Next, modify `server/config.py` to suit your needs, ensuring the `ENCODER_MODULE` and `TRANSPORT_MODULE` are properly configured and pointed to your desired modules:

## Sample config.py
```python
EXTERNAL_C2_ADDR = "127.0.0.1"
EXTERNAL_C2_PORT = "2222"
C2_PIPE_NAME = "foobar"
C2_BLOCK_TIME = 100
C2_ARCH = "x86"
IDLE_TIME = 5
ENCODER_MODULE = "encoder_b64url"
TRANSPORT_MODULE = "transport_gmail"
verbose = False
debug = False
```

Next, modify the configuration section for your selected `transport` and `encoder` module.

Ensure that `client/mechanism/$mechanism_client.py`'s configuration section matches with any configurations you have defined thus far.

On the machine running the server, execute:

`python server.py`

For more verbose output, you may run:

`python server.py -v`

For more verbose output and additional output that is useful for debugging, you may run:

`python server.py -d`

Next, execute the client on the targeted endpoint.

If everything worked, a new beacon will be registered within the Cobalt Strike console that you may interact with.

# FAQ
**Why would you write this?**:
There weren't very many released implementation of the spec, and of the ones that are released, they either are not in a language that I am familiar with or do not have the modularity and abstraction that I was seeking.

**Why Python 2?**:
I'm lazy and it's easy to implement new transport and encoding channels in it.

**Your code sucks**:
That's not a question.

**Can I submit new transport and/or encoder modules?**:
Yes please! Submit a pull request and I would be happy to review.

# Roadmap
* Similar abstraction and modularity will be implemented in the client component as well, to support different methods of process injection for the beacon payload and other features on the roadmap.

* Currently, this is missing the builder functionality, which is planned to dynamically build client and server deployments, but it is on the roadmap.
