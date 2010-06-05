from setuptools import setup
from scramble import __version__

setup(
    name = "scrambled",
    version = __version__,
    description = "Python Package Server",
    long_description = "",
    url = "http://code.google.com/p/scrambled",

    maintainer = "Brandon Gilmore",
    maintainer_email = "brandon@mg2.org",
    license = "BSD",

    platforms = "any",
    packages = [ "scramble" ],

    entry_points = {
        "console_scripts": [ "scrambled = scramble.server:run" ]
    },
)

