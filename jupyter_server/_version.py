"""
store the current version info of the server.

"""
version_info = (2, 1, 0, ".dev", "0")
__version__ = ".".join(map(str, version_info[:3])) + "".join(version_info[3:])
