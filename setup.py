# -*- coding: utf-8 -*-
"""Setup for AiiDA registry."""

from __future__ import absolute_import
from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
        name='aiida-registry',
        packages=find_packages(),
        long_description=open('README.md').read(),
        long_description_content_type='text/markdown',
        version='0.2.0',
        description='Registry of AiiDA plugins.',
        author='AiiDA Team',
        author_email='aiidateam@gmail.com',
        url='https://aiidateam.github.io/aiida-registry/',
        scripts=['bin/aiida-registry'],
        install_requires=[
            'jinja2',
            'requests',
            'requests-cache',
            'requirements-parser',
            'tomlkit~=0.5.11',
            'poetry',
            'click',
        ],
        license='MIT',
        extras_require={
            'pre-commit': [
                'pre-commit~=2.2',
                'pylint~=2.5.0',
            ],
            'testing': ['pytest'],
        },
    )
