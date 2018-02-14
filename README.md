# external_c2 framework
Python framework for building and utlizing interfaces to transfer data between frameworks, with a specific focus on serving as an extension to Command and Control frameworks.

Currently, this is only intended as an implementation of Cobalt Strike's External C2 specification as described in [this spec document](https://www.cobaltstrike.com/downloads/externalc2spec.pdf), but is subject to change as the project matures.

# Architecture
This project consists of the following main parts:
- Builder
- Skeletons
- Frameworks
- Transports
- Encoders
- Manager (not yet implemented)

## Builder
The builder reads in a config file, and uses configured options to generate a build by replacing `markers` within `skeletons`.

The builder can be used with `build_files.py`. A sample builder configuration is provided as `sample_builder_config.config.sample`.

## Skeletons
`skeletons` are the different "skeletons" of code that the `builder` will dynamically populate to generate a completely usable build. `skeletons` contain `markers` that will be replaced with usable values by the `builder`. There are three different 'types' of skeletons:

### Skeleton Markers
A marker can be placed inside any file in a `skeleton`, which will be replaced with a value specified in the builder config. In best practice, **markers should never be used to directly write variables, and should only ever be used to set values**. If a marker's value has to be reused, one should opt to store the value in a variable and reference it that way, instead of reusing the same marker.

The marker format is: ` ```[var:::identifier_for_the_marker]``` `

Strings will be written into a skeleton directly wrapped in single quotes, and numbers will be written as is.

**In the event a string in the config is wrapped in double quotes**, the string will be written directly to the file wrapped in double quotes instead, and the wrapping single quotes will be stripped.

This relationship can demonstrated as:

```python
#################
# Skeleton Code #
#################

# Skeleton contains the following line of code:
foo = ```[var:::bar]```

##############
# End Result #
##############

# Stored in config as:
#   foo = bar
# Written as:
foo = 'bar'

# Stored in config as:
#   foo = "bar"
# Written as:
foo = "bar"

# Stored in config as:
#   foo = 2
# Written as:
foo = 2

# Stored in config as:
#  foo = "2"
# Written as:
foo = "2"
```

## Frameworks
Frameworks are the base application that determines what data is being used by the `transport` and `encoder`, and how that data is used. What a specific `framework` actually does doesn't really matter, so long as logic exists to import and use the `encoder` and `transport`. Most of the essential portions of a framework (primarily `client` logic) will be stored as a `skeleton`, with an interface to interact with the server portion of it being stored as a base `framework` object.

Generally, a framework is contains a `server` and `client`, and makes use of `encoders` and `transports` to relay data between them. 

There are few fundamentals to consider when building a `framework`:
* The `framework` is responsible for ensuring that the `encoder` is made available to the `transport` to be used.
* If the `framework` uses a client-server relationship, they should be appropriately organized as such.
* Understand that in a majority of cases, the end-user will never directly interact with a framework's `client`, so if you want things to be reconfigurable on the `client`, it needs to be able to do that during runtime with no direct interaction.
* There should be little need for creating a `server` `skeleton` because the end-user is going to be directly interacting with a framework's `server`. Instead, opt to both read in options from a configuration, and give the end-user the ability to modify options (such as a block timer or vebosity) during runtime.
* A `framework` skeleton will be processed by the builder, iterating through every file in it, so if a certain argument needs to be configurable at build time, it can be easily done.
* A `framework` `server` should be able to be interfaced by a common `framework_manager`.

### Framework Server
The server is the application that brokers communication between the `client` and the `c2 server`. The server logic is primarily static. The logic for the server for the `cobalt_strike` framework, referred to as `third-party Client Controller` within the spec, is shown below:
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

A `server` should support the ability to handle multiple clients (not yet implemented), and be interfaced by a `framework_manager`.

### Framework Client
The client is essentially the payload that runs on the endpoint. The logic of the client for the `cobalt_strike` framework is primarily static, and shown below:
1. Run any preparations need to be utilizing the `transport`
2. Receive the stager
3. Inject the stager and open the handle to the beacon
4. Obtain metadata from the beacon
5. Relay the metadata from the beacon to the C2 server via the `transport`
6. Watch the `transport` for new tasks
7. Relay new tasks to the beacon
8. Relay responses from the beacon via the `transport`
9. Repeat steps 6-8.

The client makes use of the specified `encoder` and `transport` to relay data between itself and its respective `server`.

## Encoders
Encoders recieve data, then modify that data to either prepare it for use to be sent via the transport, or decode data recieved via the transport back into its raw form to be interpreted by whatever `framework` component is utilizing it.

Encoders should expect to be interfaced directly by the transport, and handle data in a framework and component agnostic manner.

## Transports
Transports serve the role of sending and receiving data through a communication channel, and interfacing with the encoder to ensure that data is transformed to whatever format is nesessary. Transports should expect to recieve data from a framework component, or via the communication channel, and have the ability to relay data through the communication channel. **Transports are responsible for calling the `encoder` to encode or decode data as nesessary**.

Transports should expect to be interfaced directly by the `framework` component, and handle data in a framework and component agnostic manner.

# How to use this
1. First, determine which transport and encoding module you'd like to use. We'll use `transport_imgur` and `encoder_lsbjpg` for the following example.

2. Next, create a `builder_config.config` to suit your needs, refer to the provided sample config and template for direction on how to do this.

3. Generate a build with `build_files.py`. As an example, one would generate a build in the `builds` directory using `encoder_lsbjpg`, and `transport_imgur` for Cobalt Strike, verbosely, with the following command:

```bash
python build_files.py -b builds -f cobalt_strike -c sample_builder_config.config.sample -e encoder_lsbjpg -t transport_imgur -v
```

4. Next, start running your built server and distribute your client.


### Cobalt Strike
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
There weren't very many released implementation of the Cobalt Strike spec, and of the ones that are released, they either are not in a language that I am familiar with or do not have the modularity and abstraction that I was seeking.

**Why Python 2?**:
I'm lazy and it's easy to implement new transport and encoding channels in it.

**Your code sucks**:
That's not a question.

**Can I submit new transport and/or encoder modules?**:
Yes please! Submit a pull request and I would be happy to review.

**How do I compile the client into an executable I can distribute?**:
I've tested this successfully in Kali, to recreate my environment, just ensure you have [veil-evasion](https://github.com/Veil-Framework/Veil-Evasion) installed and that you ran through its setup. It should have setup a wine environment with python installed that has all of the dependencies you need. You MAY have to install the `pefile` module into this environment as well.

Then, you can go to the directory for the client you want to generate an executable for and run:

```bash
chmod +x compile_dll.sh
./compile_dll.sh
wine "C:\\Python27\\python.exe" /usr/share/veil/pyinstaller/pyinstaller.py -F -r c2file.dll -w --key "ayyyyyyylmao" client.py
```

Replace the value for `key` with whatever you want. You should see the client executable in the `dist/` directory. If you want to generate an executable that provides a console that you can use for debugging, compile the executable with `wine "C:\\Python27\\python.exe" /usr/share/veil/pyinstaller/pyinstaller.py -F -r c2file.dll -c client.py`
