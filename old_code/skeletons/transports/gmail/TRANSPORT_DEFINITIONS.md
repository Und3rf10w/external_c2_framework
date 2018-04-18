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
##### transports/gmail/transport_gmail.py
```
	# The Gmail User to authenticate with and send emails to
	GMAIL_USER = ```[var:::gmail_user]```

	# The password for the above gmail user
	GMAIL_PWD = ```[var:::gmail_pwd]```

	# The gmail server to authenticate to. Use smtp.gmail.com
	SERVER = ```[var:::smtp_server]```

	# The port to cconnect to the server above on
	SERVER_PORT = ```[var:::smtp_port]```

	# The amount of time in seconds to wait before attempting to resend messages
	RETRY_TIMER = ```[var:::retry_time]```
```
