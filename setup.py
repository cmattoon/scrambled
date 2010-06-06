from setuptools import setup
from scramble import __version__

setup(
    name = "scrambled",
    version = __version__,
    description = "a PyPI-compatible package server",
    long_description = """\
About
=====

scrambled is a tiny PyPI-comptable package server that can be used to index
and serve a directory of Python packages and eggs. 

Overview
========

* No external dependencies
* Simple configuration: point it at a directory and run
* Conforms to PyPI conventions for integration with easy_install, pip, et al

Source
======

Up-to-date sources can always be found at the `scrambled GoogleCode site
<http://code.google.com/p/scrambled/>`_.
""",
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

