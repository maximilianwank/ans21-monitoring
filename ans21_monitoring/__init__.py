from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("ans21-monitoring")
except PackageNotFoundError:
    __version__ = "unknown"
