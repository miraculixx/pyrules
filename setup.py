import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='pyrules',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='commercial',  # example license
    description='python rules engine',
    long_description=README,
    url='http://www.shrebo.com/',
    author='Patrick Senti',
    author_email='patrick.senti@shrebo.ch',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: Commercial',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # replace these appropriately if you are using Python 3
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django==1.6',
        'django-reversion==1.8.5', # Latest version (1.8.6) requires django 1.8
        'pyyaml==3.11',
        'pyparsing==2.0.3',
        'celery==3.1.18',
        'django-tastypie==0.12.1',
        'tastypie-async==0.1.1',
    ],
    dependency_links=[
        'https://github.com/miraculixx/tastypie-async/archive/0.1.1.zip#egg=tastypie-async-0.1.1'
    ]
)
