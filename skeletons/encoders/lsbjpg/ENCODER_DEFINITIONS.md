# Builder replacement mapping definitions

This document lists and defines the builder definitons used for the `SkeletonHandler()` utility for documentation purposes for the framework: `cobalt_strike`.

Values marked: `# * - Defined by user` will be read in from values directly defined by the user. Values not marked as such are defined by the conditions of the environment during execution of the builder logic.

Generally unless noted otherwise, strings must be written in the config as `string`. In addition, unless noted otherwise, numbers are written as `1` and have their type forced in the code.

For example,
```python
[component]
# Will be written to the file as 'foo'
foo = foo

# Will be written to the file as '1'
bar = 1
```

## Definitions
#### encoders/lsbjpg/encoder_lsbjpg.py

```
    # The size of the image in pixel width
    img_size = ```[var:::img_size]```
    
    # The format to save the generated image in. Use r"'PNG'".
    img_format = ```[var:::img_format]```

```
----