__version__ = "unknown"
try:
    from _version import __version__
except ImportError:
    # We're running in a tree that doesn't have a version number in _version.py.
    pass

API_VERSION = '0.1'

class Client:
    pass

class Record:
    pass

class APIError:
    pass
