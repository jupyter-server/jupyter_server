"""
store the current version info of the server.

"""
version_info = (1, 13, 5, "", "")
__version__ = ".".join(map(str, version_info[:3])) + "".join(version_info[3:])
