"""
store the current version info of the server.

"""

# Downstream maintainer, when running `python.setup.py jsversion`,
# the version string is propagated to the JavaScript files,  do not forget to
# patch the JavaScript files in `.postN` release done by distributions.

# Next beta/alpha/rc release: The version number for beta is X.Y.ZbN **without dots**.
# However, be sure to INCLUDE a dot prefix when adding the dev release: X.Y.Z.devN
# See: https://www.python.org/dev/peps/pep-0440/#public-version-identifiers

version_info = (1, 4, 0, '')
__version__ = '.'.join(map(str, version_info[:3])) + ''.join(version_info[3:])
