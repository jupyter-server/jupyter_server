"""
store the current version info of the server.

"""
version_info = (2, 0, 0, "rc", "0")
__version__ = ".".join(map(str, version_info[:3])) + "".join(version_info[3:])
