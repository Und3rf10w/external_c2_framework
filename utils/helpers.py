# TODO: create a get_datetime() function that returns the current date and time


def color(string, warning=False, bold=True, yellow=False):
    """
    Change text color for the terminal, defaults to green
    Set "warning=True" for red
    """
    attr = []

    if warning or string.strip().startswith("[!]"):
        # red
        attr.append('31')
    if yellow or string.strip().startswith("[+]"):
        attr.append('33')
    if bold:
        attr.append('1')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)
