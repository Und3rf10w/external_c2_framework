# Builder replacement mapping definitions

This document lists and defines the builder definitons used for the `SkeletonHandler()` utility for documentation purposes for the framework: `cobalt_strike`.

Values marked: `# * - Defined by user` will be read in from values directly defined by the user. Values not marked as such are defined by the conditions of the environment during execution of the builder logic.

Generally unless noted otherwise, strings must be written in the config as `string`. In addition, unless noted otherwise, numbers are written as `1` and have their type forced in the code.

For example,
```python
[component]
# Will be written to the file as 'bar'
foo = bar
# Written as:
#   foo = 'bar'

# Will be written to the file as '1'
baz = 1
# Written as:
#   baz = '1'
```

For this reason, **IT IS CRITICAL YOU FORCE THE DESIRED TYPE OF YOUR VARIABLE**.

## Definitions
##### transports/imgur/transport_imgur.py

```
	# The imgur username to authenticate with
	USERNAME = ```[var:::username]```

	# The api client ID to authenticate with
	client_id = ```[var:::client_id]```

	# The client secret to autehnticate with
	client_secret = ```[var:::client_secret]```

	# The name of the album being used to transmit the stager
	STAGER_ALBUM_NAME = ```[var:::stager_album_name]```

	# The name of album being used for sending tasks
	SEND_ALBUM_NAME = ```[var:::send_album_name]```

	# The name of the album being used for receiving responses
	RECV_ALBUM_NAME = ```[var:::recv_album_name]```
	
	# The name of the album being used to signal beacon initalization
	INIT_ALBUM_NAME = ```[var:::init_album_name]```

	# A default value for the access token. Just put any string
	access_token = ```[var:::access_token]```

	# A default value for the refresh token. Just put any string
	refresh_token = ```[var:::refresh_token]```
```
----
