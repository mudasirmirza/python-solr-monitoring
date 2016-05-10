__author__ = 'yury'
from distutils.core import setup
from setuptools import find_packages
from monitoring import VERSION

setup(
    name = "solr-monitoring",
    version = VERSION,
    keywords = ("Solr monitoring"),
    description = "Solr monitoring with cloudwatch integration",
    author = "Kozyrev Yury",
    author_email = "ustarts@gmail.com",
    license = "MIT License",
    url="https://github.com/urakozz/python-solr-monitoring",
    packages = find_packages(),
    include_package_data = True,
    install_requires=['boto>=2.33.0'],
    entry_points={'console_scripts': [
        'solr_monitoring=main:main',
        ]
    },
    platforms = "python 2.7",
)
