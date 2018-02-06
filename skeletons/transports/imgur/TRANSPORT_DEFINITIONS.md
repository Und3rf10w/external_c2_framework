# Builder replacement mapping definitions

This document lists and defines the builder definitons used for the `SkeletonHandler()` utility for documentation purposes for the framework: `cobalt_strike`.

Values marked: `# * - Defined by user` will be read in from values directly defined by the user. Values not marked as such are defined by the conditions of the environment during execution of the builder logic.

Generally unless noted otherwise, strings must be written in the config as `r'"string"'`, or `r"'string'"`, depending on what you want. In addition, unless noted otherwise, numbers are written as `'1'` and have their type forced in the code.

**NOTE:** THIS MEANS YOU MUST INCLUDE QUOTES FOR YOUR STRING

## Definitions
##### transports/imgur/transport_imgur.py

```

	USERNAME = ```[var:::USERNAME]```
	client_id = ```[var:::client_id]```
	client_secret = ```[var:::client_secret]```
	SEND_ALBUM_NAME = ```[var:::SEND_ALBUM_NAME]```
	RECV_ALBUM_NAME = ```[var:::RECV_ALBUM_NAME]```
	access_token = ```[var:::access_token]```
	refresh_token = ```[var:::refresh_token]```
	STAGER_ALBUM_NAME = ```[var:::STAGER_ALBUM_NAME]```

```
----
