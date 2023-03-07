#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = ['click>=8.0.3', 'pandas>=1.3.5', 'networkx>=2.6.3', 'matplotlib>=3.5.0', 'flask==2.0.2', 'lxml>=4.7.1', 'xmltodict>=0.12.0', 'bio>=1.3.3']

test_requirements = ['pytest>=6.2.4']

setup(
    author="Justus Bisten",
    author_email='s6jubist@uni-bonn.de',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description="Mapping of Authors connected by their publications.",
    entry_points={
        'console_scripts': [
            'authormaps=authormaps.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=history,
    include_package_data=True,
    keywords='authormaps',
    name='authormaps',
    packages=find_packages(include=['authormaps', 'authormaps.*']),
    test_suite='tests',
    tests_require=test_requirements,
    version='0.1.0',
    zip_safe=False,
)
