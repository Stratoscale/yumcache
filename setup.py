import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="yumcache",
    version="1.0",
    author="Shlomo Matichin",
    author_email="shlomomatichin@gmail.com",
    description=(
        "A dumb squid-like http local cache-proxy for development environments "
        "that call package managers excessivly, like yum, npm or pip"),
    keywords="python squid http cache proxy yum npm pip",
    url="http://packages.python.org/yumcache",
    packages=['yumcache'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
    ],
    install_requires=[
        'requests',
    ],
)
