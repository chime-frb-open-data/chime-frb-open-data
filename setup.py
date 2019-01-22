"""
CHIME/FRB Open Data
"""


from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # CHIME/FRB Open Data
    name='cfod',
    version='2019.01',
    description='Python project to read CHIME/FRB Data',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://chime-frb-open-data.github.io/',
    author='CHIME/FRB Collaboration',
    author_email='charanjot.brar@mcgill.ca',

    # Classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='CHIME/FRB intensity astronomy',
    packages=find_packages(exclude=['numpy', 'msgpack-python']),
    install_requires=['numpy', 'msgpack-python'],
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={},
    project_urls={
        'Bug Reports': 'https://github.com/chime-frb-open-data/chime-frb-open-data/issues',
    },
)
