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

## Definitions
##### transports/reddit/transport_reddit.py

```
	# The api client ID to authenticate with
	CLIENT_ID = ```[var:::client_id]```

	# The api client secret to authenticate with
	CLIENT_SECRET = ```[var:::client_secret]```

	# The username to use for the specified account
	USERNAME = ```[var:::username]```

	# The password to use for the specified account
	PASSWORD = ```[var:::password]```

	# The user agent string to send with the requests
	# It is recommended that you include your username in it
	# sample: "I AM TOTALLY MALWARE by /u/"
	USER_AGENT = ```[var:::user_agent]```

	# The subject name of the PMs that have sent data
	SEND_NAME = ```[var:::send_name]```

	# The suject name of the PMs that have responses
	RECV_NAME = ```[var:::recv_name]```
```