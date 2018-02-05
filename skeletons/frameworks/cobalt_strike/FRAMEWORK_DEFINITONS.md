# Builder replacement mapping definitions

This document lists and defines the builder definitons used for the `SkeletonHandler()` utility for documentation purposes for the framework: `cobalt_strike`.

Values marked: `# * - Defined by user` will be read in from values directly defined by the user. Values not marked as such are defined by the conditions of the environment during execution of the builder logic.

Generally unless noted otherwise, strings must be written in the config as `r'"string"'`, or `r"'string'"`, depending on what you want. In addition, unless noted otherwise, numbers are written as is.

**NOTE:** THIS MEANS YOU MUST INCLUDE QUOTES FOR YOUR STRING

## Definitions
##### client/clientcore/clientcore.py
```python
    # Replaced with the source code of the selected encoder goes
    encoder_code = ```[var:::encoder_code]```
    
    # Replaced with the source code of the selected transport 
    transport_code = ```[var:::transport_code]```
    
    # Replaced with the constants that need to be defined for the client to fuctionally operate
    client_consts = ```[var:::client_consts]```
    
    # Replaced with a number that defines the amount of time the client will wait between batches of jobs
    # * - Defined by user
    c2_block_time = ```[var:::c2_block_time]``
    
    # Replaced with the name of the dll that the client will refer to the embedded dll as
    # * - Defined by user
    # Must be passed as an escaped string in r'aw' format
    cdll_name = ```[var:::cdll_name]```
```
----

##### client/clientdll/c2file_dll.c
```python
    # Replaced with the name of the pipe that the client will open for the beacon
    # * - Defined by user
    # Must be passed as an escaped string in r'aw' format
    c2_pipe_name = ```[var:::c2_pipe_name]````
```
----

##### client/clienthelpers/compile_dll.sh
```python
    # Replaced with the name of the dll that the client will refer to the embedded dll as
    # * - Defined by user
    # Must be passed as an escaped string in r'aw' format
    cdll_name = ```[var:::cdll_name]```
```
----